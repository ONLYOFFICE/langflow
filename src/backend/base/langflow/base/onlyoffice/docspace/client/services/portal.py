from __future__ import annotations
from typing import Any, Tuple
from ..base import Response, Service


class PortalService(Service):
    def get_current(self) -> Tuple[Any, Response]:
        return self._client.get(
            "api/2.0/portal",
        )
