"""Generic ERP bridge: maps high-level intents to ERP-specific operations."""

from __future__ import annotations

import logging
from typing import Any, Protocol

logger = logging.getLogger(__name__)


class ERPConnector(Protocol):
    """Anything exposing the `run(action, doctype, **kwargs)` interface, e.g. `ERPNextTool`."""

    def run(self, action: str, doctype: str, **kwargs: Any) -> Any: ...


class ERPBridge:
    """Routes high-level intents (e.g. "create a maintenance ticket") to a configured ERP connector."""

    def __init__(self, connector: ERPConnector):
        self.connector = connector

    def create_stock_entry(self, item_code: str, qty: float, warehouse: str, **extra: Any) -> Any:
        """Create a Material Receipt Stock Entry for `qty` of `item_code` into `warehouse`."""
        logger.info("ERP: creating stock entry (item=%s, qty=%s, warehouse=%s)", item_code, qty, warehouse)
        fields = {
            "stock_entry_type": "Material Receipt",
            "items": [{"item_code": item_code, "qty": qty, "t_warehouse": warehouse}],
            **extra,
        }
        return self.connector.run("create", "Stock Entry", fields=fields)

    def create_maintenance_ticket(self, subject: str, description: str, **extra: Any) -> Any:
        """Open an Issue/maintenance ticket with `subject` and `description`."""
        logger.info("ERP: creating maintenance ticket (subject=%s)", subject)
        fields = {"subject": subject, "description": description, **extra}
        return self.connector.run("create", "Issue", fields=fields)

    def get_ticket_status(self, ticket_name: str) -> Any:
        """Fetch the current state of a maintenance ticket by its name/ID."""
        logger.info("ERP: fetching ticket status (name=%s)", ticket_name)
        return self.connector.run("get", "Issue", name=ticket_name)
