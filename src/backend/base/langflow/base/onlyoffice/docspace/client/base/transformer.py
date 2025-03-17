from __future__ import annotations
from typing import Any, Callable, Protocol
from http.client import HTTPResponse
from urllib.request import Request as HTTPRequest
from .opener import Opener


TransformerHandler = Callable[[HTTPRequest], HTTPRequest]


class Transformer(Protocol):
    def transform(self, request: HTTPRequest, next: TransformerHandler) -> HTTPRequest:
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

        request = HTTPRequest(
            request.full_url,
            data=origin.data,
            method=origin.method
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
        next = self._build_chain(index + 1)

        return lambda request: current.transform(request, next)
