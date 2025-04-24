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
        api_url = self.api_url if hasattr(self, "api_url") else None
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

        if "Authorization" not in headers:
            headers["Authorization"] = f"Bearer {token}"

        if body and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode("utf-8")

        response = requests.request(    # noqa: S113
            method,
            f"{api_url}{url}",
            data=data,
            headers=headers,
        )

        try:
            result = json.loads(response.text)
        except json.JSONDecodeError:
            result = {
                "success": response.status_code == 204 and method.lower() == "delete",  # noqa: PLR2004
            }

        return result, response


class Service:
    def __init__(self, client: BaseClient):
        self._client = client
