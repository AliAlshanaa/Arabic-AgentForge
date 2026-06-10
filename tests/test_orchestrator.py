from arabic_agentforge.core import AgentOrchestrator, ArabicAgent


def _stub_completion(content):
    def completion_fn(**kwargs):
        return {"choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": content}}]}

    return completion_fn


def test_route_without_router_returns_first_registered_agent():
    agent_a = ArabicAgent(name="agent-a", model="gpt-4o", completion_fn=_stub_completion("a"))
    agent_b = ArabicAgent(name="agent-b", model="gpt-4o", completion_fn=_stub_completion("b"))

    orchestrator = AgentOrchestrator(agents=[agent_a, agent_b])

    assert orchestrator.route("أي مهمة") == "agent-a"


def test_router_agent_selects_named_agent():
    agent_a = ArabicAgent(name="agent-a", model="gpt-4o", completion_fn=_stub_completion("a"))
    agent_b = ArabicAgent(name="agent-b", model="gpt-4o", completion_fn=_stub_completion("b"))
    router = ArabicAgent(name="router", model="gpt-4o", completion_fn=_stub_completion("agent-b"))

    orchestrator = AgentOrchestrator(agents=[agent_a, agent_b], router=router)

    assert orchestrator.route("مهمة خاصة بالوكيل ب") == "agent-b"


def test_run_returns_orchestrator_result():
    agent_a = ArabicAgent(name="agent-a", model="gpt-4o", completion_fn=_stub_completion("نتيجة"))
    orchestrator = AgentOrchestrator(agents=[agent_a])

    result = orchestrator.run("مهمة")

    assert result.agent_name == "agent-a"
    assert result.response == "نتيجة"
