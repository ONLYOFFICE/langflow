from __future__ import annotations
from urllib.request import Request as HTTPRequest
from ..base import TransformerHandler


class OriginTransformer:
    def __init__(self, origin: str):
        self._origin = origin


    def transform(self, request: HTTPRequest, next: TransformerHandler) -> HTTPRequest:
        request.add_header("Origin", self._origin)
        return next(request)
