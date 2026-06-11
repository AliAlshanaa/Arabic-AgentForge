"""High-level, LLM-callable ERP actions built on top of `ERPBridge`.

`ERPNextTool` is a thin, generic REST wrapper (action/doctype/fields) - too low-level
for an LLM to call reliably. Tools in this module expose one focused action each, with
a parameter schema simple enough for the model to fill in correctly.
"""

from __future__ import annotations

from typing import Any

from ..connectors.erp_bridge import ERPBridge
from .base import BaseTool


class CreateMaintenanceTicketTool(BaseTool):
    """Lets an agent open a maintenance ticket (ERPNext "Issue") from a subject and description."""

    name = "create_maintenance_ticket"
    description = "افتح تذكرة صيانة جديدة في نظام ERP بعنوان ووصف للمشكلة."
    parameters = {
        "type": "object",
        "properties": {
            "subject": {
                "type": "string",
                "description": "عنوان مختصر للمشكلة، مثال: عطل في طابعة القسم الثالث",
            },
            "description": {
                "type": "string",
                "description": "وصف تفصيلي يساعد فريق الصيانة على فهم المشكلة والتعامل معها",
            },
        },
        "required": ["subject", "description"],
    }

    def __init__(self, bridge: ERPBridge):
        self.bridge = bridge

    def run(self, subject: str, description: str) -> Any:
        return self.bridge.create_maintenance_ticket(subject, description)
