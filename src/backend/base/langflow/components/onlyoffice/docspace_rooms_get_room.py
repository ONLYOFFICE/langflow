from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace import (
    AuthTextInput,
    Component,
    DataOutput,
    ErrorResponse,
    RoomIdInput,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.schema import Data


class OnlyofficeDocspaceGetRoom(Component):
    display_name = "Get Room"
    description = "Get a room from ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceGetRoom"


    inputs = [
        AuthTextInput(),
        RoomIdInput(info="The ID of the room to get."),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        room_id: int = Field(..., description="The ID of the room to get.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            room_id=self.room_id,
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._get_room(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_get_room",
            description="Get a room from ONLYOFFICE DocSpace.",
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return await self._get_room(schema)


    async def _get_room(self, schema: Schema) -> Any:
        client = await self._get_client()

        room, response = client.files.get_room(schema.room_id)
        if isinstance(response, ErrorResponse):
            raise response.exception

        return room
