from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace import (
    AuthTextInput,
    Component,
    DataOutput,
    ErrorResponse,
    FileIdInput,
    ToolOutput,
    UpdateFileOptions,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data


class OnlyofficeDocspaceUpdateFile(Component):
    display_name = "Update File"
    description = "Update a file in ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceUpdateFile"


    inputs = [
        AuthTextInput(),
        FileIdInput(info="The ID of the file to update."),
        MessageTextInput(
            name="title",
            display_name="Title",
            info="The new title of the file.",
        ),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
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
