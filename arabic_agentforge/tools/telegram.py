"""Telegram bot connector tool."""

from __future__ import annotations

from typing import Any

import requests

from .base import BaseTool


class TelegramTool(BaseTool):
    """Sends messages to Telegram chats via the Bot API."""

    name = "telegram"
    description = "Send a text message to a Telegram chat."

    def __init__(self, bot_token: str, timeout: int = 30):
        self.bot_token = bot_token
        self.timeout = timeout
        self._base_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(self, chat_id: str | int, text: str, parse_mode: str | None = None) -> dict[str, Any]:
        """Send `text` to `chat_id`, optionally formatted with `parse_mode` (e.g. "Markdown")."""
        payload: dict[str, Any] = {"chat_id": chat_id, "text": text}
        if parse_mode:
            payload["parse_mode"] = parse_mode
        response = requests.post(f"{self._base_url}/sendMessage", json=payload, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def get_me(self) -> dict[str, Any]:
        """Return info about this bot; useful to verify the token is valid."""
        response = requests.get(f"{self._base_url}/getMe", timeout=self.timeout)
        response.raise_for_status()
        return response.json()["result"]

    def get_updates(self, offset: int | None = None, timeout: int = 30) -> list[dict[str, Any]]:
        """Long-poll for new messages, returning Telegram `Update` objects since `offset`."""
        params: dict[str, Any] = {"timeout": timeout}
        if offset is not None:
            params["offset"] = offset
        response = requests.get(f"{self._base_url}/getUpdates", params=params, timeout=timeout + self.timeout)
        response.raise_for_status()
        return response.json()["result"]

    def run(self, chat_id: str | int, text: str, parse_mode: str | None = None) -> Any:
        return self.send_message(chat_id, text, parse_mode)
