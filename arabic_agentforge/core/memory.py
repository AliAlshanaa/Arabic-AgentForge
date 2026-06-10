"""Conversation memory for multi-turn agent interactions."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Message:
    """A single turn in a conversation."""

    role: str  # "system" | "user" | "assistant" | "tool"
    content: str
    name: str | None = None


@dataclass
class ConversationMemory:
    """Stores the rolling history of a conversation, optionally capped at `max_messages`."""

    max_messages: int | None = None
    messages: list[Message] = field(default_factory=list)

    def add(self, role: str, content: str, *, name: str | None = None) -> None:
        """Append a message and trim the oldest entries if `max_messages` is exceeded."""
        self.messages.append(Message(role=role, content=content, name=name))
        if self.max_messages is not None and len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def add_user(self, content: str) -> None:
        self.add("user", content)

    def add_assistant(self, content: str) -> None:
        self.add("assistant", content)

    def to_llm_messages(self) -> list[dict[str, str]]:
        """Return the history as a list of `{"role": ..., "content": ...}` dicts."""
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def clear(self) -> None:
        self.messages.clear()
