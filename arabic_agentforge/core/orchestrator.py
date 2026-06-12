"""Multi-agent orchestration: routes tasks to the right registered agent."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from .agent import AgentResponse, ArabicAgent

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorResult:
    """The result of running a task through the orchestrator."""

    response: str
    agent_name: str
    agent_response: AgentResponse


class AgentOrchestrator:
    """Holds a set of `ArabicAgent`s and routes incoming tasks to one of them."""

    def __init__(self, agents: list[ArabicAgent] | None = None, router: ArabicAgent | None = None):
        self.agents: dict[str, ArabicAgent] = {agent.name: agent for agent in (agents or [])}
        self.router = router

    def add_agent(self, agent: ArabicAgent) -> None:
        """Register `agent` so it can receive routed tasks."""
        self.agents[agent.name] = agent

    def route(self, task: str) -> str:
        """Return the name of the agent best suited to handle `task`.

        If a `router` agent is configured, it is asked to choose by name; otherwise
        the first registered agent is used.
        """
        if not self.agents:
            raise ValueError("no agents registered with the orchestrator")

        if self.router is not None:
            agent_names = ", ".join(self.agents)
            routing_prompt = (
                f"اختر اسم الوكيل الأنسب للمهمة التالية من بين: {agent_names}.\n"
                f"المهمة: {task}\nأجب باسم الوكيل فقط ودون أي شرح إضافي."
            )
            choice = self.router.run(routing_prompt).response.strip()
            if choice in self.agents:
                logger.info("orchestrator routed task to agent '%s'", choice)
                return choice
            logger.warning("router chose unknown agent '%s'; falling back to default", choice)

        default = next(iter(self.agents))
        logger.info("orchestrator routed task to default agent '%s'", default)
        return default

    def run(self, task: str) -> OrchestratorResult:
        """Route `task` to the appropriate agent and return its response."""
        agent_name = self.route(task)
        agent_response = self.agents[agent_name].run(task)
        return OrchestratorResult(
            response=agent_response.response,
            agent_name=agent_name,
            agent_response=agent_response,
        )
