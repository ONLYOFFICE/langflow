from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace.client import ErrorResponse, UpdateFileOptions
from langflow.base.onlyoffice.docspace.component import Component
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput, SecretStrInput
from langflow.io import Output
from langflow.schema import Data
from langflow.template import Output


class OnlyofficeDocspaceUpdateFile(Component):
    display_name = "Update File"
    description = "Update a file in ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceUpdateFile"


    inputs = [
        SecretStrInput(
            name="auth_text",
            display_name="Text from Basic Authentication",
            info="Text output from the Basic Authentication component.",
            advanced=True,
        ),
        MessageTextInput(
            name="file_id",
            display_name="File ID",
            info="The ID of the file to update.",
        ),
        MessageTextInput(
            name="title",
            display_name="Title",
            info="The new title of the file.",
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
        file_id: int = Field(..., description="The ID of the file to update.")
        title: str = Field(..., description="The new title of the file.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            file_id=self.file_id,
            title=self.title,
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._update_file(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_update_file",
            description="Update a file in ONLYOFFICE DocSpace.",
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return await self._update_file(schema)


    async def _update_file(self, schema: Schema) -> Any:
        client = await self._get_client()

        options = UpdateFileOptions(title=schema.title)

        result, response = client.files.update_file(schema.file_id, options)
        if isinstance(response, ErrorResponse):
            raise response.exception

        return result
