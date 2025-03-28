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
    UpdateRoomOptions,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data


class OnlyofficeDocspaceUpdateRoom(Component):
    display_name = "Update Room"
    description = "Update a room in ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceUpdateRoom"


    inputs = [
        AuthTextInput(),
        RoomIdInput(info="The ID of the room to update."),
        MessageTextInput(
            name="title",
            display_name="Title",
            info="The new title of the room.",
        ),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        room_id: int = Field(..., description="The ID of the room to update.")
        title: str = Field(..., description="The new title of the room.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            room_id=self.room_id,
            title=self.title,
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._update_room(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_update_room",
            description="Update a room in ONLYOFFICE DocSpace.",
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return await self._update_room(schema)


    async def _update_room(self, schema: Schema) -> Any:
        client = await self._get_client()

        options = UpdateRoomOptions(title=schema.title)

        result, response = client.files.update_room(schema.room_id, options)
        if isinstance(response, ErrorResponse):
            raise response.exception

        return result
