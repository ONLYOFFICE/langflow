from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace.client import ErrorResponse, UpdateRoomOptions
from langflow.base.onlyoffice.docspace.component import Component
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput, SecretStrInput
from langflow.io import Output
from langflow.schema import Data
from langflow.template import Output


class OnlyofficeDocspaceUpdateRoom(Component):
    display_name = "Update Room"
    description = "Update a room in ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceUpdateRoom"


    inputs = [
        SecretStrInput(
            name="auth_text",
            display_name="Text from Basic Authentication",
            info="Text output from the Basic Authentication component.",
            advanced=True,
        ),
        MessageTextInput(
            name="room_id",
            display_name="Room ID",
            info="The ID of the room to update.",
        ),
        MessageTextInput(
            name="title",
            display_name="Title",
            info="The new title of the room.",
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
