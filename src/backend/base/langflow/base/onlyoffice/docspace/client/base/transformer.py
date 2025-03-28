from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Protocol
from urllib.request import Request as HTTPRequest

if TYPE_CHECKING:
    from http.client import HTTPResponse

    from .opener import Opener


TransformerHandler = Callable[[HTTPRequest], HTTPRequest]


class Transformer(Protocol):
    def transform(self, request: HTTPRequest, follow: TransformerHandler) -> HTTPRequest:
        ...


class TransformingOpener:
    def __init__(self, opener: Opener):
        self._opener = opener
        self._transformers: list[Transformer] = []


    def __getattr__(self, name: str) -> Any:
        return getattr(self._opener, name)


    def copy(self) -> TransformingOpener:
        opener = TransformingOpener(self._opener)
        opener._transformers = self._transformers.copy()
        return opener


    def add_transformer(self, transformer: Transformer) -> None:
        self._transformers.append(transformer)


    def open(self, request: HTTPRequest, *args: Any, **kwargs: Any) -> HTTPResponse:
        if not self._transformers:
            return self._opener.open(request, *args, **kwargs)

        origin = request

        method = None
        if hasattr(origin, "method"):
            method = origin.method

        request = HTTPRequest(  # noqa: S310
            request.full_url,
            data=origin.data,
            method=method,
        )

        for key, value in origin.headers.items():
            request.add_header(key, value)

        chain = self._build_chain()
        request = chain(request)

        return self._opener.open(request, *args, **kwargs)


    def _build_chain(self, index: int = 0) -> TransformerHandler:
        if index >= len(self._transformers):
            return lambda request: request

        current = self._transformers[index]
        follow = self._build_chain(index + 1)

        return lambda request: current.transform(request, follow)
