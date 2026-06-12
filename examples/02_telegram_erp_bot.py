"""Real end-to-end example: Telegram bot -> ArabicAgent (real LLM) -> ERPNext.

A user sends a message in Arabic (any dialect) to the bot, e.g.:
    "سوّ لي تذكرة صيانة، الطابعة في القسم الثالث ما تطبع"

The agent detects the dialect, calls Gemini, decides to use the
`create_maintenance_ticket` tool, opens an "Issue" in ERPNext via
`ERPBridge`, and replies to the user in MSA confirming the ticket.

Setup
-----
Copy `.env.example` (in the project root) to `.env` and fill in:

1. Free Gemini API key: https://aistudio.google.com/apikey
       GEMINI_API_KEY=...

2. ERPNext sandbox (e.g. a free trial site at https://frappecloud.com), with an
   API key/secret generated from the user's settings:
       ERPNEXT_URL=https://your-site.frappe.cloud
       ERPNEXT_API_KEY=...
       ERPNEXT_API_SECRET=...

3. Telegram bot token from @BotFather:
       TELEGRAM_BOT_TOKEN=...

Run
---
    python examples/02_telegram_erp_bot.py
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv

from arabic_agentforge import ArabicAgent, setup_logging
from arabic_agentforge.connectors.erp_bridge import ERPBridge
from arabic_agentforge.guards import ArabicHallucinationGuard
from arabic_agentforge.tools import CreateMaintenanceTicketTool, ERPNextTool, TelegramTool

logger = logging.getLogger(__name__)

_REQUIRED_VARS = [
    "GEMINI_API_KEY",
    "TELEGRAM_BOT_TOKEN",
    "ERPNEXT_URL",
    "ERPNEXT_API_KEY",
    "ERPNEXT_API_SECRET",
]


@dataclass
class Config:
    """Required configuration for this example, loaded from the environment / `.env`."""

    telegram_bot_token: str
    erpnext_url: str
    erpnext_api_key: str
    erpnext_api_secret: str

    @classmethod
    def from_env(cls) -> "Config":
        load_dotenv()

        missing = [name for name in _REQUIRED_VARS if not os.environ.get(name)]
        if missing:
            raise SystemExit(
                "متغيرات البيئة التالية مفقودة: "
                + ", ".join(missing)
                + "\nانسخ .env.example إلى .env واملأ القيم، أو عيّنها في الـ shell."
            )

        return cls(
            telegram_bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
            erpnext_url=os.environ["ERPNEXT_URL"],
            erpnext_api_key=os.environ["ERPNEXT_API_KEY"],
            erpnext_api_secret=os.environ["ERPNEXT_API_SECRET"],
        )


def build_agent(config: Config) -> ArabicAgent:
    erpnext = ERPNextTool(
        base_url=config.erpnext_url,
        api_key=config.erpnext_api_key,
        api_secret=config.erpnext_api_secret,
    )
    bridge = ERPBridge(connector=erpnext)

    return ArabicAgent(
        name="maintenance-agent",
        model="gemini/gemini-2.5-flash",
        dialect="gulf",
        persona="موظف دعم فني يساعد الموظفين على فتح تذاكر صيانة عبر تيليجرام",
        tools=[CreateMaintenanceTicketTool(bridge=bridge)],
        hallucination_guard=ArabicHallucinationGuard(citation_required=False, confidence_threshold=0.6),
    )


def run_bot(agent: ArabicAgent, telegram: TelegramTool) -> None:
    bot_info = telegram.get_me()
    logger.info("Bot @%s is online and listening for messages. Press Ctrl+C to stop.", bot_info["username"])
    offset: int | None = None
    while True:
        for update in telegram.get_updates(offset=offset):
            offset = update["update_id"] + 1
            message = update.get("message")
            if not message or "text" not in message:
                continue

            chat_id = message["chat"]["id"]
            logger.info("received message from chat_id=%s: %s", chat_id, message["text"])
            try:
                reply = agent.run(message["text"]).response
            except Exception:
                logger.exception("error handling message from chat_id=%s", chat_id)
                reply = "عذرًا، حدث خطأ مؤقت أثناء معالجة طلبك. حاول مرة أخرى بعد قليل."

            telegram.send_message(chat_id, reply)


if __name__ == "__main__":
    setup_logging()
    config = Config.from_env()
    run_bot(build_agent(config), TelegramTool(bot_token=config.telegram_bot_token))
