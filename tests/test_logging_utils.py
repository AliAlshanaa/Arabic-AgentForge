import logging
import sys

from arabic_agentforge import setup_logging
from arabic_agentforge.logging_utils import _QUIET_LOGGERS, RedactingFilter


def test_setup_logging_adds_handler_and_sets_level():
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    original_level = root.level

    try:
        setup_logging(level=logging.DEBUG)

        assert root.level == logging.DEBUG
        assert len(root.handlers) == len(original_handlers) + 1
    finally:
        for handler in root.handlers:
            if handler not in original_handlers:
                root.removeHandler(handler)
        root.setLevel(original_level)


def test_redacting_filter_masks_message_args():
    filt = RedactingFilter(["topsecret"])
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "key=%s", ("topsecret",), None)

    filt.filter(record)

    assert record.getMessage() == "key=***"


def test_redacting_filter_masks_exception_message():
    filt = RedactingFilter(["topsecret"])
    try:
        raise ValueError("https://api.example.com?key=topsecret")
    except ValueError:
        record = logging.LogRecord("test", logging.ERROR, __file__, 1, "boom", (), sys.exc_info())

    filt.filter(record)

    assert "topsecret" not in str(record.exc_info[1])
    assert "***" in str(record.exc_info[1])


def test_setup_logging_redacts_known_env_secrets(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "shh-its-a-secret")
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    original_level = root.level

    try:
        setup_logging()

        added = [h for h in root.handlers if h not in original_handlers]
        assert len(added) == 1
        filters = [f for f in added[0].filters if isinstance(f, RedactingFilter)]
        assert len(filters) == 1
        assert "shh-its-a-secret" in filters[0]._secrets
    finally:
        for handler in root.handlers:
            if handler not in original_handlers:
                root.removeHandler(handler)
        root.setLevel(original_level)


def test_setup_logging_quiets_noisy_third_party_loggers():
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    original_level = root.level
    original_quiet_levels = {name: logging.getLogger(name).level for name in _QUIET_LOGGERS}

    try:
        setup_logging()

        for name in _QUIET_LOGGERS:
            assert logging.getLogger(name).level == logging.WARNING
    finally:
        for handler in root.handlers:
            if handler not in original_handlers:
                root.removeHandler(handler)
        root.setLevel(original_level)
        for name, level in original_quiet_levels.items():
            logging.getLogger(name).setLevel(level)
