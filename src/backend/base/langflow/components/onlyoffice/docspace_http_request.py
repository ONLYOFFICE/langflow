import json
from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace.client import ErrorResponse
from langflow.base.onlyoffice.docspace.component import Component
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput, SecretStrInput
from langflow.io import Output
from langflow.schema import Data
from langflow.template import Output


class OnlyofficeDocspaceHttpRequest(Component):
    display_name = "HTTP Request"
    description = "Make an HTTP request using ONLYOFFICE DocSpace client."
    name = "OnlyofficeDocspaceHttpRequest"


    inputs = [
        SecretStrInput(
            name="auth_text",
            display_name="Text from Basic Authentication",
            info="Text output from the Basic Authentication component.",
        ),
        MessageTextInput(
            name="method",
            display_name="Method",
            info="The HTTP method to use.",
            value="GET",
        ),
        MessageTextInput(
            name="path",
            display_name="Path",
            info="The path to make the request to.",
        ),
        MessageTextInput(
            name="query",
            display_name="Query",
            info="The query parameters of the request in JSON format.",
        ),
        MessageTextInput(
            name="body",
            display_name="Body",
            info="The body of the request in JSON format.",
        ),
    ]


    outputs = [
        Output(
            display_name="Data",
            name="api_build_data",
            method="build_data",
        ),
        Output(
            display_name="Tool",
            name="api_build_tool",
            method="build_tool",
            hidden=True,
        ),
    ]

    class Schema(BaseModel):
        method: str | None = Field(None, description="The HTTP method to use.")
        path: str | None = Field(None, description="The path to make the request to.")
        query: dict[str, str] | None = Field(None, description="The query parameters of the request.")
        body: dict[str, str] | None = Field(None, description="The body of the request.")


    def _create_schema(self) -> Schema:
        query: dict[str, str] | None = None
        if self.query:
            query = json.loads(self.query)

        body: dict[str, str] | None = None
        if self.body:
            body = json.loads(self.body)

        return self.Schema(
            method=self.method,
            path=self.path,
            query=query,
            body=body,
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._send_request(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_http_request",
            description="Make an HTTP request using ONLYOFFICE DocSpace client.",
            func=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> dict:
        schema = self.Schema(**kwargs)
        return await self._send_request(schema)


    async def _send_request(self, schema: Schema) -> Any:
        client = await self._get_client()

        payload, response = client.request(
            schema.method,
            schema.path,
            schema.query,
            schema.body,
        )

        if isinstance(response, ErrorResponse):
            raise Exception(response.error)

        return payload
