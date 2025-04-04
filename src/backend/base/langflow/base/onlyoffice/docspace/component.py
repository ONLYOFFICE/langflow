import os
from urllib.parse import urlparse, urlunparse

from langflow.base.onlyoffice.docspace.client import Client
from langflow.base.onlyoffice.docspace.mixins import AuthTextMixin
from langflow.custom import Component as BaseComponent

_ROUTER_VARIABLE_NAME = "API_ROUTER_HOST"
_ORIGIN_VARIABLE_NAME = "origin"
_AUTH_KEY_VARIABLE_NAME = "asc_auth_key"


class Component(BaseComponent, AuthTextMixin):
    display_name = "Docspace Component"
    description = "Component to interact with ONLYOFFICE DocSpace."
    icon = "onlyoffice"


    async def _get_client(self) -> Client:
        client = Client()

        if self.auth_text:
            try:
                client.base_url = self.auth_text["base_url"]
                client = client.with_auth_token(self.auth_text["token"])

            except Exception as e:
                msg = "Failed to create client from auth_text"
                raise ValueError(msg) from e

        else:
            try:
                router = os.environ.get(_ROUTER_VARIABLE_NAME)

                try:
                    origin = await self.get_variables(_ORIGIN_VARIABLE_NAME, "")
                except:  # noqa: E722
                    origin = None

                if router and origin:
                    if not _is_url(router):
                        msg = f"{_ROUTER_VARIABLE_NAME} environment variable is not a valid URL"
                        raise ValueError(msg)

                    if not _is_url(origin):
                        msg = f"{_ORIGIN_VARIABLE_NAME} LangFlow variable is not a valid URL"
                        raise ValueError(msg)

                    client.base_url = _append_trailing_slash(router)
                    client = client.with_origin(origin)

                elif router and not origin:
                    if not _is_url(router):
                        msg = f"{_ROUTER_VARIABLE_NAME} environment variable is not a valid URL"
                        raise ValueError(msg)

                    client.base_url = _append_trailing_slash(router)

                elif not router and origin:
                    if not _is_url(origin):
                        msg = f"{_ORIGIN_VARIABLE_NAME} LangFlow variable is not a valid URL"
                        raise ValueError(msg)

                    client.base_url = _append_trailing_slash(origin)
                    client = client.with_origin(origin)

                elif not router and not origin:
                    msg = f"{_ROUTER_VARIABLE_NAME} environment variable is not set and {_ORIGIN_VARIABLE_NAME} LangFlow variable is not set"
                    raise ValueError(msg)

                try:
                    key = await self.get_variables(_AUTH_KEY_VARIABLE_NAME, "")
                except:  # noqa: E722
                    key = None

                if not key:
                    msg = f"{_AUTH_KEY_VARIABLE_NAME} LangFlow variable is not set"
                    raise ValueError(msg)

                client = client.with_auth_token(key)

            except Exception as e:
                msg = "Failed to create client from environment variables"
                raise ValueError(msg) from e

        return client


def _is_url(value: str) -> bool:
    try:
        url = urlparse(value)
        return all([url.scheme, url.netloc])
    except:  # noqa: E722
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
