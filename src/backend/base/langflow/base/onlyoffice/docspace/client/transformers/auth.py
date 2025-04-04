from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from urllib.request import Request as HTTPRequest

    from langflow.base.onlyoffice.docspace.client.base import TransformerHandler


class AuthTokenTransformer:
    def __init__(self, token: str):
        self._token = token


    def transform(self, request: HTTPRequest, follow: TransformerHandler) -> HTTPRequest:
        request.add_header("Authorization", self._token)
        return follow(request)
