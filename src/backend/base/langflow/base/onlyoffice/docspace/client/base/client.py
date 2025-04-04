from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Self
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request as HTTPRequest
from urllib.request import build_opener

from .response import ErrorPayload, ErrorResponse, Response, SuccessPayload, SuccessResponse
from .transformer import Transformer, TransformingOpener

if TYPE_CHECKING:
    from .opener import Opener


class Client:
    @property
    def opener(self) -> Opener:
        return self._opener.copy()


    def __init__(self, opener: Opener | None = None):
        self.base_url = ""
        self.user_agent = ""

        origin = opener if opener else build_opener()
        self._opener = TransformingOpener(origin)


    def _with_transformer(self, transformer: Transformer) -> Self:
        client = self._copy()
        client._opener.add_transformer(transformer)
        return client


    def _copy(self) -> Self:
        client = self.__class__(self._opener)
        client.base_url = self.base_url
        client.user_agent = self.user_agent
        client._opener = self._opener.copy()
        return client


    def delete(
        self,
        path: str,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
    ) -> tuple[Any, Response]:
        return self.request("DELETE", path, query, headers, body)


    def get(
        self,
        path: str,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[Any, Response]:
        return self.request("GET", path, query, headers)


    def post(
        self,
        path: str,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
    ) -> tuple[Any, Response]:
        return self.request("POST", path, query, headers, body)


    def put(
        self,
        path: str,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
    ) -> tuple[Any, Response]:
        return self.request("PUT", path, query, headers, body)


    def request(
        self,
        method: str,
        path: str,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
    ) -> tuple[Any, Response]:
        url = self.create_url(path, query)
        request = self.create_request(method, url, headers, body)
        body, response = self.send_request(request)
        return body, response


    def create_url(self, path: str, query: dict[str, Any] | None = None) -> str:
        if not self.base_url.endswith("/"):
            msg = f"Base URL must have a trailing slash, but {self.base_url} does not"
            raise ValueError(msg)

        if path.startswith("/"):
            msg = f"URL path must not have a leading slash, but {path} does"
            raise ValueError(msg)

        url = urljoin(self.base_url, path)

        if query:
            enc = urlencode(query)
            if enc:
                url = f"{url}?{enc}"

        return url


    def create_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
    ) -> HTTPRequest:
        data = json.dumps(body).encode("utf-8") if body else None

        request = HTTPRequest(url, data=data, method=method)  # noqa: S310

        request.add_header("Accept", "application/json")

        if body:
            request.add_header("Content-Type", "application/json")

        if self.user_agent:
            request.add_header("User-Agent", self.user_agent)

        if headers:
            for key, value in headers.items():
                request.add_header(key, value)

        return request


    def send_request(self, request: HTTPRequest) -> tuple[Any, Response]:
        wrapper: Response

        try:
            with self._opener.open(request) as response:
                content = response.read()
                wrapper = SuccessResponse(request, response)
                wrapper.payload = SuccessPayload.model_validate_json(content)

        except HTTPError as error:
            with error:
                content = error.read()
                wrapper = ErrorResponse(request, error)
                wrapper.payload = ErrorPayload.model_validate_json(content)

        except URLError as error:
            wrapper = ErrorResponse(request, error)

        except Exception as error:  # noqa: BLE001
            wrapper = ErrorResponse(request, error)

        return wrapper.content, wrapper
