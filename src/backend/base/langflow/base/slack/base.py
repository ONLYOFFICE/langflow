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

        if headers is None:
            headers = {}

        headers["Accept"] = "application/json"
        headers["Authorization"] = f"Bearer {self.auth}"

        if body and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode("utf-8")

        response = requests.request(    # noqa: S113
            method,
            url,
            data=data,
            headers=headers,
        )

        result = json.loads(response.text)

        return result, response


class Service:
    def __init__(self, client: BaseClient):
        self._client = client
