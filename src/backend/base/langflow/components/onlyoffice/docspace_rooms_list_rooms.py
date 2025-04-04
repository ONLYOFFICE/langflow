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


class OnlyofficeDocspaceListRooms(Component):
    display_name = "List Rooms"
    description = "List rooms in ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceListRooms"


    inputs = [
        AuthTextInput(),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        pass


    async def build_data(self) -> Data:
        data = await self._list_rooms()
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_list_rooms",
            description="List rooms in ONLYOFFICE DocSpace.",
            coroutine=self._list_rooms,
            args_schema=self.Schema,
        )


    async def _list_rooms(self) -> Any:
        client = await self._get_client()

        ls, response = client.files.list_rooms()
        if isinstance(response, ErrorResponse):
            raise response.exception

        return ls
