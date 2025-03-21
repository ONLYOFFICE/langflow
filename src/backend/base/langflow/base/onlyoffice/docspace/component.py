import json
import os
from urllib.parse import urlparse, urlunparse

from langflow.base.onlyoffice.docspace.client import Client
from langflow.custom import Component as BaseComponent

_ROUTER_VARIABLE_NAME = "API_ROUTER_HOST"
_ORIGIN_VARIABLE_NAME = "origin"
_AUTH_KEY_VARIABLE_NAME = "asc_auth_key"


class Component(BaseComponent):
    display_name = "Docspace Component"
    description = "Component to interact with ONLYOFFICE DocSpace."
    icon = "onlyoffice"

    auth_text: str | None


    async def _get_client(self) -> Client:
        client = Client()

        if self.auth_text:
            try:
                auth = json.loads(self.auth_text)
                client.base_url = auth["base_url"]
                client = client.with_auth_token(auth["token"])

            except Exception as e:
                raise ValueError("Failed to create client from auth_text") from e

        else:
            try:
                router = os.environ.get(_ROUTER_VARIABLE_NAME)

                try:
                    origin = await self.get_variables(_ORIGIN_VARIABLE_NAME, "")
                except:
                    origin = None

                if router and origin:
                    if not _is_url(router):
                        raise ValueError(f"{_ROUTER_VARIABLE_NAME} environment variable is not a valid URL")
                    if not _is_url(origin):
                        raise ValueError(f"{_ORIGIN_VARIABLE_NAME} LangFlow variable is not a valid URL")
                    client.base_url = _append_trailing_slash(router)
                    client = client.with_origin(origin)

                elif router and not origin:
                    if not _is_url(router):
                        raise ValueError(f"{_ROUTER_VARIABLE_NAME} environment variable is not a valid URL")
                    client.base_url = _append_trailing_slash(router)

                elif not router and origin:
                    if not _is_url(origin):
                        raise ValueError(f"{_ORIGIN_VARIABLE_NAME} LangFlow variable is not a valid URL")
                    client.base_url = _append_trailing_slash(origin)
                    client = client.with_origin(origin)

                elif not router and not origin:
                    raise ValueError(f"{_ROUTER_VARIABLE_NAME} environment variable is not set and {_ORIGIN_VARIABLE_NAME} LangFlow variable is not set")

                try:
                    key = await self.get_variables(_AUTH_KEY_VARIABLE_NAME, "")
                except:
                    key = None

                if not key:
                    raise ValueError(f"{_AUTH_KEY_VARIABLE_NAME} LangFlow variable is not set")
                client = client.with_auth_token(key)

            except Exception as e:
                raise ValueError("Failed to create client from environment variables") from e

        return client


def _is_url(value: str) -> bool:
    try:
        url = urlparse(value)
        return all([url.scheme, url.netloc])
    except:
        return False


def _append_trailing_slash(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path

    if not path:
        path = "/"
    elif not path.endswith("/"):
        path = path + "/"

    new = parsed._replace(path=path)
    return urlunparse(new)
