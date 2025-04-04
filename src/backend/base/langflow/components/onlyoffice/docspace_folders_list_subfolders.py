from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace import (
    AuthTextInput,
    Component,
    DataOutput,
    ErrorResponse,
    FolderIdInput,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.schema import Data


class OnlyofficeDocspaceListSubfolders(Component):
    display_name = "List Subfolders"
    description = "List subfolders in ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceListSubfolders"


    inputs = [
        AuthTextInput(),
        FolderIdInput(info="The ID of the folder to list subfolders for."),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        folder_id: int = Field(..., description="The ID of the folder to list subfolders for.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            folder_id=self.folder_id,
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        return [Data(data=data) for data in await self._list_subfolders(schema)]


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_list_subfolders",
            description="List subfolders in ONLYOFFICE DocSpace.",
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return await self._get_room(schema)


    async def _list_subfolders(self, schema: Schema) -> list[Any]:
        client = await self._get_client()

        result, response = client.files.list_subfolders(schema.folder_id)
        if isinstance(response, ErrorResponse):
            raise response.exception

        return result
