import json
from typing import Any

import requests


class BaseClient:
    def request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None
    ) -> tuple[Any | None, requests.Response]:
        data = body

        if hasattr(self, "auth_text") and self.auth_text:
            token = self.auth_text["token"]
            api_url = self.auth_text["api_url"]

        if not api_url:
            msg = "API URL is not provided"
            raise ValueError(msg)

        if headers is None:
            headers = {}

        headers["Accept"] = "application/json"

        if "x-api-token" not in headers:
            headers["x-api-token"] = token

        if body and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
            data = json.dumps({k: v for k, v in body.items() if v != ""}).encode("utf-8")

        response = requests.request(    # noqa: S113
            method,
            f"{api_url}{url}",
            data=data,
            headers=headers,
        )

        result = json.loads(response.text)

        return result, response


class Service:
    def __init__(self, client: BaseClient):
        self._client = client
