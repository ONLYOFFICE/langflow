import json
from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace.client import ErrorResponse, Invitation, SetRoomAccessRightOptions
from langflow.base.onlyoffice.docspace.component import Component
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput, SecretStrInput
from langflow.schema import Data
from langflow.template import Output


class OnlyofficeDocspaceSetRoomAccessRights(Component):
    display_name = "Set Room Access Rights"
    description = "Set access rights to a room in ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceSetRoomAccessRights"


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
            info="The ID of the room to set access rights.",
        ),
        MessageTextInput(
            name="invitations",
            display_name="Invitations",
            info="The list of invitations to set in JSON format.",
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
        room_id: int = Field(..., description="The ID of the room to set access rights.")
        invitations: list[Invitation] = Field(..., description="The list of invitations to set.")


    def _create_schema(self) -> Schema:
        room_id: int | None = None
        if self.room_id:
            room_id = int(self.room_id)

        invitations: list[Invitation] | None = None
        if self.invitations:
            invitations = json.loads(self.invitations)

        return self.Schema(
            room_id=room_id,
            invitations=invitations,
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._set_room_access_rights(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_set_room_access_rights",
            description="Set access rights to a room in ONLYOFFICE DocSpace.",
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return await self._set_room_access_rights(schema)


    async def _set_room_access_rights(self, schema: Schema) -> Any:
        client = await self._get_client()

        options = SetRoomAccessRightOptions(
            invitations=schema.invitations,
        )

        result, response = client.rooms.set_room_access_right(
            schema.room_id,
            options,
        )

        if isinstance(response, ErrorResponse):
            raise response.exception

        return result
