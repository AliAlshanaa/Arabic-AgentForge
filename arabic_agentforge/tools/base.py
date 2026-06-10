"""Base interface for tools that agents can invoke."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """A capability an agent can call, e.g. an ERP, chat, or automation integration."""

    name: str
    description: str

    @abstractmethod
    def run(self, **kwargs: Any) -> Any:
        """Execute the tool and return a JSON-serializable result."""

    def to_schema(self) -> dict[str, Any]:
        """Return an OpenAI/LiteLLM-compatible function-calling schema for this tool."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {"type": "object", "properties": {}, "additionalProperties": True},
            },
        }
