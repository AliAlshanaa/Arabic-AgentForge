"""Console logging setup for applications built on Arabic AgentForge."""

from __future__ import annotations

import logging
import os
from collections.abc import Iterable

# Third-party loggers that are noisy at INFO level and rarely useful to end users.
_QUIET_LOGGERS = ["LiteLLM", "httpx", "httpcore", "urllib3"]

# Environment variables that commonly hold API keys/tokens; their values are masked
# in log output by default so they don't leak into recordings or shared terminals.
_SECRET_ENV_VARS = [
    "GEMINI_API_KEY",
    "GROQ_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "TELEGRAM_BOT_TOKEN",
    "ERPNEXT_API_KEY",
    "ERPNEXT_API_SECRET",
]


class RedactingFilter(logging.Filter):
    """Masks configured secret values wherever they appear in a log record.

    Covers both the log message and any attached exception's message, so a secret
    embedded in e.g. a request URL inside a traceback is masked too.
    """

    def __init__(self, secrets: Iterable[str]) -> None:
        super().__init__()
        self._secrets = [s for s in dict.fromkeys(secrets) if s]

    def filter(self, record: logging.LogRecord) -> bool:
        if not self._secrets:
            return True

        original = record.getMessage()
        redacted = self._redact(original)
        if redacted != original:
            record.msg = redacted
            record.args = ()

        exc_value = record.exc_info[1] if record.exc_info else None
        if exc_value is not None:
            if exc_value.args:
                exc_value.args = tuple(
                    self._redact(arg) if isinstance(arg, str) else arg for arg in exc_value.args
                )
            message = getattr(exc_value, "message", None)
            if isinstance(message, str):
                exc_value.message = self._redact(message)

        return True

    def _redact(self, text: str) -> str:
        for secret in self._secrets:
            text = text.replace(secret, "***")
        return text


def _collect_secrets() -> list[str]:
    """Read known secret values from the environment for redaction."""
    return [value for name in _SECRET_ENV_VARS if (value := os.environ.get(name))]


def setup_logging(level: int = logging.INFO, *, redact_secrets: bool = True) -> None:
    """Configure readable, colored console logging for `arabic_agentforge` and your app.

    Uses `rich` for colored levels and pretty tracebacks if it's installed (add the
    `examples` extra to get it), falling back to a plain formatter otherwise. Also
    quiets noisy third-party loggers (LiteLLM, httpx, ...) so your app's own logs,
    set up via `logging.getLogger(__name__)`, stand out.

    By default (`redact_secrets=True`), known API keys/tokens read from the environment
    (e.g. `GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `ERPNEXT_API_KEY`) are masked as `***`
    wherever they appear in log messages or exception text - useful when sharing a
    terminal or recording a demo.
    """
    try:
        from rich.logging import RichHandler

        handler: logging.Handler = RichHandler(rich_tracebacks=True, show_path=False)
        formatter = logging.Formatter("%(message)s", datefmt="[%X]")
    except ImportError:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)-8s %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

    handler.setFormatter(formatter)

    if redact_secrets:
        handler.addFilter(RedactingFilter(_collect_secrets()))

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)

    for name in _QUIET_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)
