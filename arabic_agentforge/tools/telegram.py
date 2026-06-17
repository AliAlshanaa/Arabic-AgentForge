"""Telegram bot connector tool."""

from __future__ import annotations

import logging
from typing import Any

import requests

from .base import BaseTool

logger = logging.getLogger(__name__)


class TelegramTool(BaseTool):
    """Sends messages to Telegram chats via the Bot API."""

    name = "telegram"
    description = "Send a text message to a Telegram chat."
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "chat_id": {
                "type": "string",
                "description": "Telegram chat ID to send the message to.",
            },
            "text": {
                "type": "string",
                "description": "The message text to send.",
            },
            "parse_mode": {
                "type": "string",
                "enum": ["Markdown", "HTML"],
                "description": "Optional formatting mode.",
            },
        },
        "required": ["chat_id", "text"],
    }

    def __init__(self, bot_token: str, timeout: int = 30):
        self.bot_token = bot_token
        self.timeout = timeout
        self._base_url = f"https://api.telegram.org/bot{bot_token}"
        self._session = requests.Session()

    @staticmethod
    def _check_response(body: dict[str, Any]) -> None:
        if not body.get("ok"):
            desc = body.get("description", "unknown error")
            code = body.get("error_code", "?")
            raise ValueError(f"Telegram API error {code}: {desc}")

    def send_message(self, chat_id: str | int, text: str, parse_mode: str | None = None) -> dict[str, Any]:
        """Send `text` to `chat_id`, optionally formatted with `parse_mode` (e.g. "Markdown")."""
        logger.info("Telegram: sending message to chat_id=%s (%d chars)", chat_id, len(text))
        payload: dict[str, Any] = {"chat_id": chat_id, "text": text}
        if parse_mode:
            payload["parse_mode"] = parse_mode
        response = self._session.post(f"{self._base_url}/sendMessage", json=payload, timeout=self.timeout)
        response.raise_for_status()
        body = response.json()
        self._check_response(body)
        return body

    def get_me(self) -> dict[str, Any]:
        """Return info about this bot; useful to verify the token is valid."""
        response = self._session.get(f"{self._base_url}/getMe", timeout=self.timeout)
        response.raise_for_status()
        body = response.json()
        self._check_response(body)
        return body["result"]

    def get_updates(self, offset: int | None = None, timeout: int = 30) -> list[dict[str, Any]]:
        """Long-poll for new messages, returning Telegram `Update` objects since `offset`."""
        logger.debug("Telegram: polling for updates (offset=%s)", offset)
        params: dict[str, Any] = {"timeout": timeout}
        if offset is not None:
            params["offset"] = offset
        response = self._session.get(f"{self._base_url}/getUpdates", params=params, timeout=timeout + self.timeout)
        response.raise_for_status()
        body = response.json()
        self._check_response(body)
        updates = body["result"]
        if updates:
            logger.debug("Telegram: received %d update(s)", len(updates))
        return updates

    def run(self, chat_id: str | int, text: str, parse_mode: str | None = None) -> Any:
        return self.send_message(chat_id, text, parse_mode)
