from __future__ import annotations
from urllib.request import Request as HTTPRequest
from ..base import TransformerHandler


class AuthTokenTransformer:
    def __init__(self, token: str):
        self._token = token


    def transform(self, request: HTTPRequest, next: TransformerHandler) -> HTTPRequest:
        request.add_header("Authorization", self._token)
        return next(request)
