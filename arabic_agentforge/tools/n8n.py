"""n8n webhook connector tool."""

from __future__ import annotations

from typing import Any

import requests

from .base import BaseTool


class N8nTool(BaseTool):
    """Triggers an n8n automation workflow via its webhook URL."""

    name = "n8n"
    description = "Trigger an n8n automation workflow with a JSON payload."

    def __init__(self, webhook_url: str, timeout: int = 30):
        self.webhook_url = webhook_url
        self.timeout = timeout

    def trigger(self, payload: dict[str, Any]) -> Any:
        """POST `payload` to the configured n8n webhook and return its response."""
        response = requests.post(self.webhook_url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        if "application/json" in response.headers.get("content-type", ""):
            return response.json()
        return response.text

    def run(self, **payload: Any) -> Any:
        return self.trigger(payload)
