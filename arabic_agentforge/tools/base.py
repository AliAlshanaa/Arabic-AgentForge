"""Base interface for tools that agents can invoke."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """A capability an agent can call, e.g. an ERP, chat, or automation integration."""

    name: str
    description: str

    # JSON Schema for `run()`'s keyword arguments, in OpenAI function-calling format.
    # Subclasses should override this with their actual parameters so the LLM knows
    # what arguments to pass; an empty schema means "call with no arguments".
    parameters: dict[str, Any] = {"type": "object", "properties": {}, "required": []}

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
                "parameters": self.parameters,
            },
        }
