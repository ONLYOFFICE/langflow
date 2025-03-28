from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace import (
    AuthTextInput,
    Component,
    DataOutput,
    DeleteFileOptions,
    ErrorResponse,
    FileIdInput,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.schema import Data


class OnlyofficeDocspaceStartDeletingFile(Component):
    display_name = "Start Deleting File"
    description = "Start asynchronous operation to delete a file from ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceStartDeletingFile"


    inputs = [
        AuthTextInput(),
        FileIdInput(info="The ID of the file to delete."),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        file_id: int = Field(..., description="The ID of the file to delete.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            file_id=self.file_id,
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        return [Data(data=data) for data in await self._start_deleting_file(schema)]


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_start_deleting_file",
            description="Start asynchronous operation to delete a file from ONLYOFFICE DocSpace.",
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return await self._start_deleting_file(schema)


    async def _start_deleting_file(self, schema: Schema) -> Any:
        client = await self._get_client()

        options = DeleteFileOptions(DeleteAfter=False, immediately=False)

        operations, response = client.files.delete_file(schema.file_id, options)
        if isinstance(response, ErrorResponse):
            raise response.exception

        return [operation.model_dump(exclude_none=True, by_alias=True) \
            for operation in operations]
