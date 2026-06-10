from unittest.mock import MagicMock, patch

import pytest

from arabic_agentforge.tools import ERPNextTool, N8nTool, TelegramTool


def test_erpnext_sets_auth_header_when_credentials_provided():
    tool = ERPNextTool(base_url="https://erp.example.com", api_key="key", api_secret="secret")
    assert tool._session.headers["Authorization"] == "token key:secret"


def test_erpnext_get_doc():
    tool = ERPNextTool(base_url="https://erp.example.com")
    tool._session = MagicMock()
    tool._session.get.return_value.json.return_value = {"data": {"name": "ISS-0001"}}
    tool._session.get.return_value.raise_for_status.return_value = None

    result = tool.get_doc("Issue", "ISS-0001")

    assert result == {"name": "ISS-0001"}
    tool._session.get.assert_called_once_with(
        "https://erp.example.com/api/resource/Issue/ISS-0001", timeout=30
    )


def test_erpnext_create_doc_via_run():
    tool = ERPNextTool(base_url="https://erp.example.com")
    tool._session = MagicMock()
    tool._session.post.return_value.json.return_value = {"data": {"name": "ISS-0002"}}
    tool._session.post.return_value.raise_for_status.return_value = None

    result = tool.run("create", "Issue", fields={"subject": "Printer broken"})

    assert result == {"name": "ISS-0002"}
    tool._session.post.assert_called_once_with(
        "https://erp.example.com/api/resource/Issue",
        json={"subject": "Printer broken"},
        timeout=30,
    )


def test_erpnext_list_docs_with_filters():
    tool = ERPNextTool(base_url="https://erp.example.com")
    tool._session = MagicMock()
    tool._session.get.return_value.json.return_value = {"data": [{"name": "ISS-0001"}]}
    tool._session.get.return_value.raise_for_status.return_value = None

    result = tool.run("list", "Issue", filters={"status": "Open"}, limit=5)

    assert result == [{"name": "ISS-0001"}]


def test_erpnext_unsupported_action_raises():
    tool = ERPNextTool(base_url="https://erp.example.com")
    with pytest.raises(ValueError):
        tool.run("delete", "Issue", name="ISS-0001")


def test_telegram_send_message():
    tool = TelegramTool(bot_token="123:ABC")
    with patch("arabic_agentforge.tools.telegram.requests.post") as mock_post:
        mock_post.return_value.json.return_value = {"ok": True}
        mock_post.return_value.raise_for_status.return_value = None

        result = tool.run(chat_id=42, text="مرحبا")

        assert result == {"ok": True}
        mock_post.assert_called_once_with(
            "https://api.telegram.org/bot123:ABC/sendMessage",
            json={"chat_id": 42, "text": "مرحبا"},
            timeout=30,
        )


def test_n8n_trigger_returns_json_response():
    tool = N8nTool(webhook_url="https://n8n.example.com/webhook/abc")
    with patch("arabic_agentforge.tools.n8n.requests.post") as mock_post:
        mock_post.return_value.headers = {"content-type": "application/json"}
        mock_post.return_value.json.return_value = {"status": "queued"}
        mock_post.return_value.raise_for_status.return_value = None

        result = tool.run(item_code="PRT-001", qty=50)

        assert result == {"status": "queued"}
        mock_post.assert_called_once_with(
            "https://n8n.example.com/webhook/abc",
            json={"item_code": "PRT-001", "qty": 50},
            timeout=30,
        )
