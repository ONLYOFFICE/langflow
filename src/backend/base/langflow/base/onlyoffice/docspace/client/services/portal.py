from __future__ import annotations

from typing import Any

from langflow.base.onlyoffice.docspace.client.base import Response, Service


class PortalService(Service):
    def get_current(self) -> tuple[Any, Response]:
        return self._client.get(
            "api/2.0/portal",
        )
