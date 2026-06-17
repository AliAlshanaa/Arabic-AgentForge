"""The base Arabic-native agent: an LLM wrapped with Arabic NLP, tools, and guards."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Callable

from ..guards.citation import Citation
from ..guards.hallucination import ArabicHallucinationGuard, GuardResult
from ..nlp.arabic_processor import ArabicTextProcessor
from ..nlp.dialect_handler import Dialect, DialectHandler
from ..tools.base import BaseTool
from .memory import ConversationMemory

logger = logging.getLogger(__name__)

_DEFAULT_SYSTEM_PROMPT = (
    "أنت مساعد ذكاء اصطناعي يتحدث العربية بطلاقة ويفهم اللهجات المحلية. "
    "أجب دائما باللغة العربية الفصحى ما لم يُطلب منك خلاف ذلك، "
    "واستشهد بمصادرك بصيغة [1]، [2] عند توفرها."
)


@dataclass
class AgentResponse:
    """The result of a single `ArabicAgent.run()` call."""

    response: str
    detected_dialect: Dialect
    citations: list[Citation] = field(default_factory=list)
    guard_result: GuardResult | None = None


class ArabicAgent:
    """An LLM-backed agent with Arabic text handling, tool calling, and a hallucination guard."""

    # Safety cap on back-and-forth tool calls within a single `run()`, in case the
    # model keeps requesting tools instead of producing a final answer.
    MAX_TOOL_ITERATIONS = 5

    def __init__(
        self,
        name: str,
        model: str,
        dialect: str | Dialect = Dialect.MSA,
        persona: str | None = None,
        system_prompt: str | None = None,
        hallucination_guard: ArabicHallucinationGuard | None = None,
        tools: list[BaseTool] | None = None,
        memory: ConversationMemory | None = None,
        knowledge_base: str | None = None,
        response_language: str = "arabic",
        completion_fn: Callable[..., Any] | None = None,
    ):
        self.name = name
        self.model = model
        self.dialect = Dialect(dialect.lower()) if isinstance(dialect, str) else dialect
        self.persona = persona
        self.system_prompt = system_prompt or _DEFAULT_SYSTEM_PROMPT
        self.hallucination_guard = hallucination_guard
        self.tools: dict[str, BaseTool] = {tool.name: tool for tool in (tools or [])}
        self.memory = memory or ConversationMemory()
        self.knowledge_base = knowledge_base
        self.response_language = response_language

        self._processor = ArabicTextProcessor()
        self._dialect_handler = DialectHandler()
        self._completion_fn = completion_fn or self._default_completion

    def add_tool(self, tool: BaseTool) -> None:
        """Register a tool the agent can call during `run()`."""
        self.tools[tool.name] = tool

    def _default_completion(self, **kwargs: Any) -> Any:
        # Imported lazily so the package is usable without litellm installed/configured
        # when callers supply their own `completion_fn`.
        from litellm import completion

        # Providers occasionally return transient 503s under load; retry a couple of
        # times before surfacing the error to the caller.
        return completion(num_retries=2, **kwargs)

    def _build_messages(self, task: str) -> list[dict[str, str]]:
        system_parts = [self.system_prompt]
        if self.persona:
            system_parts.append(f"شخصيتك: {self.persona}")
        if self.response_language:
            system_parts.append(f"لغة الرد المطلوبة: {self.response_language}")
        if self.knowledge_base:
            system_parts.append(f"اعتمد على قاعدة المعرفة التالية عند الإجابة: {self.knowledge_base}")

        messages = [{"role": "system", "content": "\n".join(system_parts)}]
        messages.extend(self.memory.to_llm_messages())
        messages.append({"role": "user", "content": task})
        return messages

    def run(self, task: str, sources: list[Citation] | None = None) -> AgentResponse:
        """Run `task` through the agent's LLM, executing any tool calls, and return the response."""
        normalized_task = self._processor.normalize_for_matching(task)
        detected_dialect = self._dialect_handler.detect(normalized_task)
        logger.info("agent '%s' received task (dialect=%s): %s", self.name, detected_dialect.value, task)

        messages = self._build_messages(task)
        kwargs: dict[str, Any] = {"model": self.model}
        if self.tools:
            kwargs["tools"] = [tool.to_schema() for tool in self.tools.values()]

        result = self._call_model(messages, **kwargs)

        for iteration in range(self.MAX_TOOL_ITERATIONS):
            tool_calls = self._extract_tool_calls(result)
            if not tool_calls:
                break

            logger.info(
                "agent '%s' requested %d tool call(s) (iteration %d/%d)",
                self.name, len(tool_calls), iteration + 1, self.MAX_TOOL_ITERATIONS,
            )
            messages.append(self._extract_message(result))
            for call in tool_calls:
                tool_result = self._execute_tool_call(call)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call["id"],
                        "content": json.dumps(tool_result, ensure_ascii=False),
                    }
                )
            result = self._call_model(messages, **kwargs)

        content = self._extract_content(result)
        logger.info("agent '%s' produced response (%d chars)", self.name, len(content))

        self.memory.add_user(task)
        self.memory.add_assistant(content)

        guard_result = None
        if self.hallucination_guard is not None:
            confidence = self._estimate_confidence(result)
            guard_result = self.hallucination_guard.check(content, confidence=confidence, sources=sources)
            if guard_result.passed:
                logger.info("agent '%s' hallucination guard passed (confidence=%.2f)", self.name, confidence)
            else:
                logger.warning("agent '%s' hallucination guard failed: %s", self.name, guard_result.reason)

        return AgentResponse(
            response=content,
            detected_dialect=detected_dialect,
            citations=sources or [],
            guard_result=guard_result,
        )

    def _call_model(self, messages: list[dict[str, Any]], **kwargs: Any) -> Any:
        """Call the LLM via `_completion_fn`, logging the request for debugging."""
        logger.debug("agent '%s' calling model '%s' with %d message(s)", self.name, self.model, len(messages))
        return self._completion_fn(messages=messages, **kwargs)

    def _execute_tool_call(self, call: dict[str, Any]) -> Any:
        """Run the tool requested by `call` and return a JSON-serializable result."""
        tool = self.tools.get(call["name"])
        if tool is None:
            logger.warning("agent '%s' requested unknown tool '%s'", self.name, call["name"])
            return {"error": f"unknown tool: {call['name']}"}

        logger.info("agent '%s' calling tool '%s' with args=%s", self.name, call["name"], call["arguments"])
        try:
            result = tool.run(**call["arguments"])
            logger.debug("agent '%s' tool '%s' returned: %s", self.name, call["name"], result)
            return result
        except Exception as exc:  # let the model see the error and decide how to recover
            logger.exception("agent '%s' tool '%s' raised an error", self.name, call["name"])
            return {"error": str(exc)}

    @staticmethod
    def _get(obj: Any, key: str, default: Any = None) -> Any:
        """Read `key` from `obj`, whether it's a dict or an object (e.g. litellm's response types)."""
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    @classmethod
    def _first_choice(cls, result: Any) -> Any:
        choices = cls._get(result, "choices") or []
        if not choices:
            raise ValueError("LLM returned no choices")
        return choices[0]

    @classmethod
    def _extract_content(cls, result: Any) -> str:
        choice = cls._first_choice(result)
        message = cls._get(choice, "message")
        return cls._get(message, "content") or ""

    @classmethod
    def _extract_message(cls, result: Any) -> dict[str, Any]:
        """Return the assistant message from `result` as a plain dict, including any tool calls."""
        choice = cls._first_choice(result)
        message = cls._get(choice, "message")

        message_dict: dict[str, Any] = {
            "role": cls._get(message, "role", "assistant"),
            "content": cls._get(message, "content"),
        }
        tool_calls = cls._get(message, "tool_calls")
        if tool_calls:
            message_dict["tool_calls"] = [
                {
                    "id": cls._get(call, "id"),
                    "type": "function",
                    "function": {
                        "name": cls._get(cls._get(call, "function"), "name"),
                        "arguments": cls._get(cls._get(call, "function"), "arguments"),
                    },
                }
                for call in tool_calls
            ]
        return message_dict

    @classmethod
    def _extract_tool_calls(cls, result: Any) -> list[dict[str, Any]]:
        """Return `[{"id", "name", "arguments"}, ...]` for any tool calls the model requested."""
        choice = cls._first_choice(result)
        message = cls._get(choice, "message")
        tool_calls = cls._get(message, "tool_calls") or []

        parsed = []
        for call in tool_calls:
            function = cls._get(call, "function")
            try:
                arguments = json.loads(cls._get(function, "arguments") or "{}")
            except json.JSONDecodeError:
                arguments = {}
            parsed.append({"id": cls._get(call, "id"), "name": cls._get(function, "name"), "arguments": arguments})
        return parsed

    @classmethod
    def _estimate_confidence(cls, result: Any) -> float:
        choice = cls._first_choice(result)
        finish_reason = cls._get(choice, "finish_reason")

        if finish_reason != "stop":
            return 0.3

        content = cls._get(cls._get(choice, "message"), "content") or ""
        score = 0.7
        if len(content) > 20:
            score += 0.1
        if re.search(r"\[\d+\]", content):
            score += 0.1
        if len(content) > 100:
            score += 0.1

        return min(score, 1.0)
