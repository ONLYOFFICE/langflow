from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace import (
    AuthTextInput,
    Component,
    CreateRoomOptions,
    DataOutput,
    ErrorResponse,
    RoomType,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data


class OnlyofficeDocspaceCreateRoom(Component):
    display_name = "Create Room"
    description = "Create a room in ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceCreateRoom"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="room_type",
            display_name="Room Type",
            info="The type of the room. The available types are: FillingFormsRoom (1), EditingRoom (2), CustomRoom (5), PublicRoom (6), VirtualDataRoom (8).",
            advanced=True,
            value="PublicRoom",
        ),
        MessageTextInput(
            name="title",
            display_name="Title",
            info="The title of the room.",
        ),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        room_type: RoomType = Field("PublicRoom", description="The type of the room.")
        title: str = Field(..., description="The title of the room.")


    def _create_schema(self) -> Schema:
        room_type = self.room_type
        try:
            room_type = int(self.room_type)
        except:  # noqa: E722
            room_type = self.room_type

        return self.Schema(
            room_type=room_type,
            title=self.title,
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._create_room(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_create_room",
            description="Create a room in ONLYOFFICE DocSpace.",
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return await self._create_room(schema)


    async def _create_room(self, schema: Schema) -> Any:
        client = await self._get_client()

        options = CreateRoomOptions(
            roomType=schema.room_type,
            title=schema.title,
        )

        room, response = client.files.create_room(options)
        if isinstance(response, ErrorResponse):
            raise response.exception

        return room
