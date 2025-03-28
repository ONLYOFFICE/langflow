from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client


class Service:
    def __init__(self, client: Client):
        self._client = client
