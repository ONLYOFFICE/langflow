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
)
from langflow.field_typing import Tool
from langflow.schema import Data


class OnlyofficeDocspaceGetFile(Component):
    display_name = "Get File"
    description = "Get a file from ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceGetFile"


    inputs = [
        AuthTextInput(),
        FileIdInput(info="The ID of the file to get."),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        file_id: int = Field(..., description="The ID of the file to get.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            file_id=self.file_id,
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._get_file(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_get_file",
            description="Get a file from ONLYOFFICE DocSpace.",
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return self._get_file(schema)


    async def _get_file(self, schema: Schema) -> Any:
        client = await self._get_client()

        result, response = client.files.get_file(schema.file_id)
        if isinstance(response, ErrorResponse):
            raise response.exception

        return result
