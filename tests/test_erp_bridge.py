from unittest.mock import MagicMock

from arabic_agentforge.connectors import ERPBridge


def test_create_stock_entry_calls_connector():
    connector = MagicMock()
    bridge = ERPBridge(connector)

    bridge.create_stock_entry(item_code="PRT-001", qty=50, warehouse="Riyadh - WH")

    connector.run.assert_called_once_with(
        "create",
        "Stock Entry",
        fields={
            "stock_entry_type": "Material Receipt",
            "items": [{"item_code": "PRT-001", "qty": 50, "t_warehouse": "Riyadh - WH"}],
        },
    )


def test_create_maintenance_ticket_calls_connector():
    connector = MagicMock()
    bridge = ERPBridge(connector)

    bridge.create_maintenance_ticket(subject="Printer broken", description="Dept 3 printer not working")

    connector.run.assert_called_once_with(
        "create",
        "Issue",
        fields={"subject": "Printer broken", "description": "Dept 3 printer not working"},
    )


def test_get_ticket_status_calls_connector():
    connector = MagicMock()
    bridge = ERPBridge(connector)

    bridge.get_ticket_status("ISS-0001")

    connector.run.assert_called_once_with("get", "Issue", name="ISS-0001")
