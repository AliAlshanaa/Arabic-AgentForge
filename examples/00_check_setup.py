"""Connectivity check for the Telegram + Gemini + ERPNext example.

Run this after filling in `.env` to confirm each service is reachable
before starting `02_telegram_erp_bot.py`.

    python examples/00_check_setup.py
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

from arabic_agentforge.tools import ERPNextTool, TelegramTool

sys.stdout.reconfigure(encoding="utf-8")


def check_telegram(token: str) -> None:
    bot = TelegramTool(bot_token=token).get_me()
    print(f"[OK] Telegram: متصل كبوت @{bot['username']}")


def check_erpnext(url: str, api_key: str, api_secret: str) -> None:
    erpnext = ERPNextTool(base_url=url, api_key=api_key, api_secret=api_secret)
    erpnext.list_docs("User", limit=1)
    print("[OK] ERPNext: الاتصال والمصادقة ناجحة")


def check_gemini() -> None:
    from litellm import completion

    completion(model="gemini/gemini-2.5-flash", messages=[{"role": "user", "content": "قل: تم"}])
    print("[OK] Gemini: مفتاح API صالح")


if __name__ == "__main__":
    load_dotenv()

    for name, check in [
        ("Telegram", lambda: check_telegram(os.environ["TELEGRAM_BOT_TOKEN"])),
        (
            "ERPNext",
            lambda: check_erpnext(
                os.environ["ERPNEXT_URL"], os.environ["ERPNEXT_API_KEY"], os.environ["ERPNEXT_API_SECRET"]
            ),
        ),
        ("Gemini", check_gemini),
    ]:
        try:
            check()
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}")
