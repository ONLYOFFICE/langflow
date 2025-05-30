import json
from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace import (
    AuthTextInput,
    Component,
    DataOutput,
    ErrorResponse,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data


class OnlyofficeDocspaceHttpRequest(Component):
    display_name = "HTTP Request"
    description = "Make an HTTP request using ONLYOFFICE DocSpace client."
    name = "OnlyofficeDocspaceHttpRequest"


    inputs = [
        AuthTextInput(),
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
            name="headers",
            display_name="Headers",
            info="The headers of the request in JSON format.",
        ),
        MessageTextInput(
            name="body",
            display_name="Body",
            info="The body of the request in JSON format.",
        ),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        method: str | None = Field(None, description="The HTTP method to use.")
        path: str | None = Field(None, description="The path to make the request to.")
        query: dict[str, str] | None = Field(None, description="The query parameters of the request.")
        headers: dict[str, str] | None = Field(None, description="The headers of the request.")
        body: dict[str, str] | None = Field(None, description="The body of the request.")


    def _create_schema(self) -> Schema:
        query: dict[str, str] | None = None
        if self.query:
            query = json.loads(self.query)

        headers: dict[str, str] | None = None
        if self.headers:
            headers = json.loads(self.headers)

        body: dict[str, str] | None = None
        if self.body:
            body = json.loads(self.body)

        return self.Schema(
            method=self.method,
            path=self.path,
            query=query,
            headers=headers,
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
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> dict:
        schema = self.Schema(**kwargs)
        return await self._send_request(schema)


    async def _send_request(self, schema: Schema) -> Any:
        client = await self._get_client()

        result, response = client.request(
            schema.method,
            schema.path,
            schema.query,
            schema.headers,
            schema.body,
        )

        if isinstance(response, ErrorResponse):
            raise response.exception

        return result
