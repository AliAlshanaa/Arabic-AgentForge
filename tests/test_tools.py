from unittest.mock import MagicMock, patch

import pytest

from arabic_agentforge.connectors.erp_bridge import ERPBridge
from arabic_agentforge.tools import CreateMaintenanceTicketTool, ERPNextTool, N8nTool, TelegramTool


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
    tool._session = MagicMock()
    tool._session.post.return_value.json.return_value = {"ok": True}
    tool._session.post.return_value.raise_for_status.return_value = None

    result = tool.run(chat_id=42, text="مرحبا")

    assert result == {"ok": True}
    tool._session.post.assert_called_once_with(
        "https://api.telegram.org/bot123:ABC/sendMessage",
        json={"chat_id": 42, "text": "مرحبا"},
        timeout=30,
    )


def test_telegram_get_me():
    tool = TelegramTool(bot_token="123:ABC")
    tool._session = MagicMock()
    tool._session.get.return_value.json.return_value = {"ok": True, "result": {"username": "my_bot"}}
    tool._session.get.return_value.raise_for_status.return_value = None

    result = tool.get_me()

    assert result == {"username": "my_bot"}
    tool._session.get.assert_called_once_with("https://api.telegram.org/bot123:ABC/getMe", timeout=30)


def test_telegram_get_updates():
    tool = TelegramTool(bot_token="123:ABC")
    tool._session = MagicMock()
    tool._session.get.return_value.json.return_value = {"ok": True, "result": [{"update_id": 1}]}
    tool._session.get.return_value.raise_for_status.return_value = None

    result = tool.get_updates(offset=1)

    assert result == [{"update_id": 1}]
    tool._session.get.assert_called_once_with(
        "https://api.telegram.org/bot123:ABC/getUpdates",
        params={"timeout": 30, "offset": 1},
        timeout=60,
    )


def test_create_maintenance_ticket_tool_schema_has_required_parameters():
    tool = CreateMaintenanceTicketTool(bridge=MagicMock())

    schema = tool.to_schema()

    assert schema["function"]["name"] == "create_maintenance_ticket"
    assert set(schema["function"]["parameters"]["properties"]) == {"subject", "description"}
    assert schema["function"]["parameters"]["required"] == ["subject", "description"]


def test_create_maintenance_ticket_tool_run_calls_bridge():
    connector = MagicMock()
    connector.run.return_value = {"name": "ISS-0003"}
    bridge = ERPBridge(connector)
    tool = CreateMaintenanceTicketTool(bridge=bridge)

    result = tool.run(subject="عطل طابعة", description="الطابعة لا تعمل في القسم الثالث")

    assert result == {"name": "ISS-0003"}
    connector.run.assert_called_once_with(
        "create",
        "Issue",
        fields={"subject": "عطل طابعة", "description": "الطابعة لا تعمل في القسم الثالث"},
    )


def test_n8n_trigger_returns_json_response():
    tool = N8nTool(webhook_url="https://n8n.example.com/webhook/abc")
    with patch("arabic_agentforge.tools.n8n.requests.post") as mock_post:
        mock_post.return_value.headers = {"content-type": "application/json"}
        mock_post.return_value.json.return_value = {"status": "queued"}
        mock_post.return_value.raise_for_status.return_value = None

        result = tool.run(payload={"item_code": "PRT-001", "qty": 50})

        assert result == {"status": "queued"}
        mock_post.assert_called_once_with(
            "https://n8n.example.com/webhook/abc",
            json={"item_code": "PRT-001", "qty": 50},
            timeout=30,
        )
