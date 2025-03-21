from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace.client import DeleteFileOptions, ErrorResponse
from langflow.base.onlyoffice.docspace.component import Component
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput, SecretStrInput
from langflow.io import Output
from langflow.schema import Data
from langflow.template import Output


class OnlyofficeDocspaceStartDeletingFile(Component):
    display_name = "Start Deleting File"
    description = "Start asynchronous operation to delete a file from ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceStartDeletingFile"


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
            info="The ID of the file to delete.",
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
        file_id: int = Field(..., description="The ID of the file to delete.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            file_id=self.file_id,
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._delete_file(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_start_deleting_file",
            description="Start asynchronous operation to delete a file from ONLYOFFICE DocSpace.",
            func=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return await self._start_deleting_file(schema)


    async def _start_deleting_file(self, schema: Schema) -> Any:
        client = await self._get_client()

        options = DeleteFileOptions(DeleteAfter=True, immediately=True)

        result, response = client.files.delete_file(schema.file_id, options)
        if isinstance(response, ErrorResponse):
            raise response.exception

        return result
