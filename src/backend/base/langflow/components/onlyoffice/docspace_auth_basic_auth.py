import hashlib
import json
from urllib.parse import urljoin

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
import requests

from langflow.custom.custom_component.component_with_cache import ComponentWithCache
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput, SecretStrInput
from langflow.schema import Data
from langflow.schema.message import Message
from langflow.services.cache.utils import CacheMiss
from langflow.template import Output


SHARED_COMPONENT_CACHE_TOKEN_KEY = "onlyoffice_docspace_basic_authorization_token"


class OnlyofficeDocspaceBasicAuthentication(ComponentWithCache):
    display_name = "Basic Authentication"
    description = "Basic authentication for ONLYOFFICE DocSpace."
    icon = "onlyoffice"
    name = "OnlyofficeDocspaceBasicAuthentication"


    inputs = [
        MessageTextInput(
            name="base_url",
            display_name="ONLYOFFICE DocSpace Base URL",
            info="The base URL of the ONLYOFFICE DocSpace instance.",
        ),
        MessageTextInput(
            name="username",
            display_name="ONLYOFFICE DocSpace Username",
            info="The username to access the ONLYOFFICE DocSpace API.",
        ),
        SecretStrInput(
            name="password",
            display_name="ONLYOFFICE DocSpace Password",
            info="The password to access the ONLYOFFICE DocSpace API.",
            value="ONLYOFFICE_DOCSPACE_PASSWORD",
        ),
    ]


    outputs = [
        Output(
            display_name="Data",
            name="api_build_data",
            method="build_data",
        ),
        Output(
            display_name="Message",
            name="api_build_message",
            method="build_message",
            hidden=True,
        ),
        Output(
            display_name="Text",
            name="api_build_text",
            method="build_text",
            hidden=True,
        ),
        Output(
            display_name="Tool",
            name="api_build_tool",
            method="build_tool",
            hidden=True,
        ),
    ]


    class Schema(BaseModel):
        base_url: str = Field(..., description="The base URL of the ONLYOFFICE DocSpace instance.")
        username: str = Field(..., description="The username to access the ONLYOFFICE DocSpace API.")
        password: str = Field(..., description="The password to access the ONLYOFFICE DocSpace API.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            base_url=self.base_url,
            username=self.username,
            password=self.password,
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._do_basic(schema)
        return Data(data=data)


    def build_message(self) -> Message:
        schema = self._create_schema()
        data = self._do_basic(schema)
        text = f"Base URL: {data["base_url"]}\n"
        text += f"Token: {data["token"]}"
        return Message(text=text)


    def build_text(self) -> Message:
        schema = self._create_schema()
        data = self._do_basic(schema)
        text = json.dumps(data, indent=4)
        return Message(text=text)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_basic_authorization",
            description="Basic authentication for ONLYOFFICE DocSpace.",
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> dict:
        schema = self.Schema(**kwargs)
        return self._do_basic(schema)


    def _do_basic(self, schema: Schema) -> dict:
        token = self._get_token(schema)
        data = {
            "base_url": schema.base_url,
            "token": token,
        }
        return data


    def _get_token(self, schema: Schema) -> str:
        key = self._create_key(schema)
        return self._ensure_token(schema, key)


    def _create_key(self, schema: Schema) -> str:
        digest = self._create_digest(schema)
        return f"{SHARED_COMPONENT_CACHE_TOKEN_KEY}_{digest}"


    def _create_digest(self, schema: Schema) -> str:
        schema = self.Schema(
            base_url=schema.base_url,
            username=schema.username,
            password="REDACTED",
        )
        json = schema.model_dump_json()
        hash = hashlib.sha1(json.encode())
        return hash.hexdigest()


    def _ensure_token(self, schema: Schema, key: str) -> str:
        token = self._retrieve_token(key)
        if not token or not self._check_auth(schema, token):
            token = self._do_auth(schema)
            self._cache_token(key, token)
        return token


    def _retrieve_token(self, key: str) -> str:
        token = self._shared_component_cache.get(key)
        if isinstance(token, CacheMiss):
            return ""
        return token


    def _cache_token(self, key: str, token: str):
        self._shared_component_cache.set(key, token)


    def _do_auth(self, schema: Schema) -> str:
        url = urljoin(schema.base_url, "api/2.0/authentication")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        body = {
            "UserName": schema.username,
            "Password": schema.password,
        }
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()["response"]["token"]


    def _check_auth(self, schema: Schema, token: str) -> bool:
        url = urljoin(schema.base_url, "api/2.0/authentication")
        headers = {
            "Accept": "application/json",
            "Authorization": f"{token}",
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()["response"]
