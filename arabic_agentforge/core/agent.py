"""The base Arabic-native agent: an LLM wrapped with Arabic NLP, tools, and guards."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from ..guards.citation import Citation
from ..guards.hallucination import ArabicHallucinationGuard, GuardResult
from ..nlp.arabic_processor import ArabicTextProcessor
from ..nlp.dialect_handler import Dialect, DialectHandler
from ..tools.base import BaseTool
from .memory import ConversationMemory

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
        self.dialect = Dialect(dialect) if isinstance(dialect, str) else dialect
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

        return completion(**kwargs)

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
        """Run `task` through the agent's LLM, returning the response, citations, and guard result."""
        normalized_task = self._processor.normalize(task, strip_diacritics=False)
        detected_dialect = self._dialect_handler.detect(normalized_task)

        messages = self._build_messages(task)
        kwargs: dict[str, Any] = {"model": self.model, "messages": messages}
        if self.tools:
            kwargs["tools"] = [tool.to_schema() for tool in self.tools.values()]

        result = self._completion_fn(**kwargs)
        content = self._extract_content(result)

        self.memory.add_user(task)
        self.memory.add_assistant(content)

        guard_result = None
        if self.hallucination_guard is not None:
            confidence = self._estimate_confidence(result)
            guard_result = self.hallucination_guard.check(content, confidence=confidence, sources=sources)

        return AgentResponse(
            response=content,
            detected_dialect=detected_dialect,
            citations=sources or [],
            guard_result=guard_result,
        )

    @staticmethod
    def _extract_content(result: Any) -> str:
        choice = result["choices"][0]
        message = choice["message"] if isinstance(choice, dict) else choice.message
        content = message["content"] if isinstance(message, dict) else message.content
        return content or ""

    @staticmethod
    def _estimate_confidence(result: Any) -> float:
        choice = result["choices"][0]
        finish_reason = choice["finish_reason"] if isinstance(choice, dict) else choice.finish_reason
        return 1.0 if finish_reason == "stop" else 0.5
