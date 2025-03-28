from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from urllib.request import Request as HTTPRequest

    from langflow.base.onlyoffice.docspace.client.base import TransformerHandler


class OriginTransformer:
    def __init__(self, origin: str):
        self._origin = origin


    def transform(self, request: HTTPRequest, follow: TransformerHandler) -> HTTPRequest:
        request.add_header("Origin", self._origin)
        return follow(request)
