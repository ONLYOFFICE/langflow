from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from http.client import HTTPResponse
    from urllib.request import Request


class Opener(Protocol):
    def open(self, request: Request, *args: Any, **kwargs: Any) -> HTTPResponse:
        ...
