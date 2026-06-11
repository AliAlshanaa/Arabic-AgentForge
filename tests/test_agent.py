import json
from unittest.mock import patch

from arabic_agentforge.core import ArabicAgent
from arabic_agentforge.guards import ArabicHallucinationGuard, Citation
from arabic_agentforge.nlp import Dialect
from arabic_agentforge.tools.base import BaseTool


def _stub_completion(content="رد تجريبي", finish_reason="stop"):
    captured: dict = {}

    def completion_fn(**kwargs):
        captured["kwargs"] = kwargs
        return {
            "choices": [
                {
                    "finish_reason": finish_reason,
                    "message": {"role": "assistant", "content": content},
                }
            ]
        }

    return completion_fn, captured


class _EchoTool(BaseTool):
    name = "echo"
    description = "Echo back the input."

    def run(self, **kwargs):
        return kwargs


def test_run_returns_response_and_detected_dialect():
    completion_fn, _ = _stub_completion(content="تم تنفيذ المهمة [1].")
    agent = ArabicAgent(name="agent", model="gpt-4o", completion_fn=completion_fn)

    result = agent.run("وش الأخبار اليوم؟")

    assert result.response == "تم تنفيذ المهمة [1]."
    assert result.detected_dialect == Dialect.GULF


def test_run_updates_conversation_memory():
    completion_fn, _ = _stub_completion(content="رد")
    agent = ArabicAgent(name="agent", model="gpt-4o", completion_fn=completion_fn)

    agent.run("سؤال")

    messages = agent.memory.to_llm_messages()
    assert messages[-2] == {"role": "user", "content": "سؤال"}
    assert messages[-1] == {"role": "assistant", "content": "رد"}


def test_hallucination_guard_passes_with_valid_citation():
    completion_fn, _ = _stub_completion(content="تمت العملية بنجاح [1].")
    agent = ArabicAgent(
        name="agent",
        model="gpt-4o",
        completion_fn=completion_fn,
        hallucination_guard=ArabicHallucinationGuard(citation_required=True, confidence_threshold=0.85),
    )

    sources = [Citation(source="ERPNext Issue #442")]
    result = agent.run("نفذ المهمة", sources=sources)

    assert result.guard_result.passed is True


def test_hallucination_guard_fails_without_citation():
    completion_fn, _ = _stub_completion(content="تمت العملية بنجاح.")
    agent = ArabicAgent(
        name="agent",
        model="gpt-4o",
        completion_fn=completion_fn,
        hallucination_guard=ArabicHallucinationGuard(citation_required=True, confidence_threshold=0.85),
    )

    result = agent.run("نفذ المهمة")

    assert result.guard_result.passed is False


def test_low_finish_reason_confidence_fails_guard():
    completion_fn, _ = _stub_completion(content="تمت العملية بنجاح [1].", finish_reason="length")
    agent = ArabicAgent(
        name="agent",
        model="gpt-4o",
        completion_fn=completion_fn,
        hallucination_guard=ArabicHallucinationGuard(citation_required=True, confidence_threshold=0.85),
    )

    sources = [Citation(source="ERPNext Issue #442")]
    result = agent.run("نفذ المهمة", sources=sources)

    assert result.guard_result.passed is False
    assert "confidence" in result.guard_result.reason


def test_default_completion_retries_transient_errors():
    agent = ArabicAgent(name="agent", model="gpt-4o")

    with patch("litellm.completion") as mock_completion:
        mock_completion.return_value = {
            "choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": "رد"}}]
        }
        agent.run("سؤال")

    assert mock_completion.call_args.kwargs["num_retries"] == 2


def test_tools_are_passed_to_completion_as_schema():
    completion_fn, captured = _stub_completion(content="تم")
    agent = ArabicAgent(name="agent", model="gpt-4o", completion_fn=completion_fn)
    agent.add_tool(_EchoTool())

    agent.run("سؤال")

    assert captured["kwargs"]["tools"][0]["function"]["name"] == "echo"


def _tool_call_response(name="echo", arguments='{"x": 1}', call_id="call_1"):
    return {
        "choices": [
            {
                "finish_reason": "tool_calls",
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {"id": call_id, "type": "function", "function": {"name": name, "arguments": arguments}}
                    ],
                },
            }
        ]
    }


def test_agent_executes_tool_call_and_returns_final_response():
    calls = []

    def completion_fn(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            return _tool_call_response()
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"role": "assistant", "content": "تم تنفيذ الأداة [1]."},
                }
            ]
        }

    agent = ArabicAgent(name="agent", model="gpt-4o", completion_fn=completion_fn)
    agent.add_tool(_EchoTool())

    result = agent.run("نفذ الأداة")

    assert result.response == "تم تنفيذ الأداة [1]."
    assert len(calls) == 2

    tool_messages = [m for m in calls[1]["messages"] if m["role"] == "tool"]
    assert tool_messages[0]["tool_call_id"] == "call_1"
    assert json.loads(tool_messages[0]["content"]) == {"x": 1}


def test_agent_reports_error_for_unknown_tool_call():
    calls = []

    def completion_fn(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            return _tool_call_response(name="not_registered")
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"role": "assistant", "content": "تعذر تنفيذ الطلب."},
                }
            ]
        }

    agent = ArabicAgent(name="agent", model="gpt-4o", completion_fn=completion_fn)
    agent.add_tool(_EchoTool())

    result = agent.run("نفذ أداة غير موجودة")

    assert result.response == "تعذر تنفيذ الطلب."
    tool_messages = [m for m in calls[1]["messages"] if m["role"] == "tool"]
    assert "error" in json.loads(tool_messages[0]["content"])
