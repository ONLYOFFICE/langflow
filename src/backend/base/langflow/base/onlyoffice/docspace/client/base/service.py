from __future__ import annotations
from .client import Client


class Service:
    def __init__(self, client: Client):
        self._client = client
