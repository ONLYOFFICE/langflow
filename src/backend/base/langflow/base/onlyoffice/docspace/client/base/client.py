from __future__ import annotations
from typing import Any, Self, Tuple
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request as HTTPRequest, build_opener
from .opener import Opener
from .response import ErrorPayload, ErrorResponse, Response, SuccessPayload, SuccessResponse
from .transformer import Transformer, TransformingOpener


class Client:
    @property
    def opener(self) -> Opener:
        return self._opener.copy()


    def __init__(self, opener: Opener | None = None):
        self.base_url = ""
        self.user_agent = ""

        origin: Opener

        if opener:
            origin = opener
        else:
            origin = build_opener()

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
    ) -> Tuple[Any, Response]:
        return self.request("DELETE", path, query, headers, body)


    def get(
        self,
        path: str,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Tuple[Any, Response]:
        return self.request("GET", path, query, headers)


    def post(
        self,
        path: str,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
    ) -> Tuple[Any, Response]:
        return self.request("POST", path, query, headers, body)


    def put(
        self,
        path: str,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
    ) -> Tuple[Any, Response]:
        return self.request("PUT", path, query, headers, body)


    def request(
        self,
        method: str,
        path: str,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
    ) -> Tuple[Any, Response]:
        url = self.create_url(path, query)
        request = self.create_request(method, url, headers, body)
        body, response = self.send_request(request)
        return body, response


    def create_url(self, path: str, query: dict[str, Any] | None = None) -> str:
        if not self.base_url.endswith("/"):
            raise ValueError(f"Base URL must have a trailing slash, but {self.base_url} does not")

        if path.startswith("/"):
            raise ValueError(f"URL path must not have a leading slash, but {path} does")

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
        if body:
            data = json.dumps(body).encode("utf-8")
        else:
            data = None

        request = HTTPRequest(url, data=data, method=method)

        request.add_header("Accept", "application/json")

        if body:
            request.add_header("Content-Type", "application/json")

        if self.user_agent:
            request.add_header("User-Agent", self.user_agent)

        if headers:
            for key, value in headers.items():
                request.add_header(key, value)

        return request


    def send_request(self, request: HTTPRequest) -> Tuple[Any, Response]:
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

        except Exception as error:
            wrapper = ErrorResponse(request, error)

        return wrapper.content, wrapper
