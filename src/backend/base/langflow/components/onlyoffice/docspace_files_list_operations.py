from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel

from langflow.base.onlyoffice.docspace import (
    AuthTextInput,
    Component,
    DataOutput,
    ErrorResponse,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.schema import Data


class OnlyofficeDocspaceListOperations(Component):
    display_name = "List Operations"
    description = "List active operations in ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceListOperations"


    inputs = [
        AuthTextInput(),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        pass


    async def build_data(self) -> list[Data]:
        return [Data(data=data) for data in await self._list_operations()]


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_list_operations",
            description="List active operations in ONLYOFFICE DocSpace.",
            coroutine=self._list_operations,
            args_schema=self.Schema,
        )


    async def _list_operations(self) -> list[Any]:
        client = await self._get_client()

        result, response = client.files.list_operations()
        if isinstance(response, ErrorResponse):
            raise response.exception

        return result
