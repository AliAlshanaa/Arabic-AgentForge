"""Generic connectors that bridge agent intents to external enterprise systems."""

from .erp_bridge import ERPBridge, ERPConnector

__all__ = ["ERPBridge", "ERPConnector"]
