"""ERPNext connector tool."""

from __future__ import annotations

from typing import Any

import requests

from .base import BaseTool


class ERPNextTool(BaseTool):
    """Reads and writes ERPNext documents through its REST API."""

    name = "erpnext"
    description = "Create, read, and list documents (e.g. Stock Entry, Issue) in ERPNext."

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        api_secret: str | None = None,
        arabic_fields: bool = False,
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.arabic_fields = arabic_fields
        self.timeout = timeout
        self._session = requests.Session()
        if api_key and api_secret:
            self._session.headers["Authorization"] = f"token {api_key}:{api_secret}"

    def _url(self, doctype: str, name: str | None = None) -> str:
        path = f"/api/resource/{doctype}"
        if name:
            path += f"/{name}"
        return f"{self.base_url}{path}"

    def get_doc(self, doctype: str, name: str) -> dict[str, Any]:
        """Fetch a single ERPNext document by doctype and name."""
        response = self._session.get(self._url(doctype, name), timeout=self.timeout)
        response.raise_for_status()
        return response.json()["data"]

    def create_doc(self, doctype: str, fields: dict[str, Any]) -> dict[str, Any]:
        """Create a new ERPNext document of `doctype` with the given `fields`."""
        response = self._session.post(self._url(doctype), json=fields, timeout=self.timeout)
        response.raise_for_status()
        return response.json()["data"]

    def list_docs(
        self,
        doctype: str,
        filters: dict[str, Any] | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """List ERPNext documents of `doctype`, optionally filtered by exact field matches."""
        params: dict[str, Any] = {"limit_page_length": limit}
        if filters:
            params["filters"] = str([[key, "=", value] for key, value in filters.items()])
        response = self._session.get(self._url(doctype), params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()["data"]

    def run(self, action: str, doctype: str, **kwargs: Any) -> Any:
        """Dispatch a "get", "create", or "list" action against ERPNext."""
        if action == "get":
            return self.get_doc(doctype, kwargs["name"])
        if action == "create":
            return self.create_doc(doctype, kwargs["fields"])
        if action == "list":
            return self.list_docs(doctype, kwargs.get("filters"), kwargs.get("limit", 20))
        raise ValueError(f"Unsupported ERPNext action: {action!r}")
