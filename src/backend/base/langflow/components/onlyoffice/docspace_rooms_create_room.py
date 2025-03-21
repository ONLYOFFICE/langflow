from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace.client import CreateRoomOptions, ErrorResponse
from langflow.base.onlyoffice.docspace.component import Component
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput, SecretStrInput
from langflow.io import Output
from langflow.schema import Data
from langflow.template import Output


class OnlyofficeDocspaceCreateRoom(Component):
    display_name = "Create Room"
    description = "Create a room in ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceCreateRoom"


    inputs = [
        SecretStrInput(
            name="auth_text",
            display_name="Text from Basic Authentication",
            info="Text output from the Basic Authentication component.",
            advanced=True,
        ),
        MessageTextInput(
            name="title",
            display_name="Title",
            info="The title of the room.",
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
        title: str = Field(..., description="The title of the room.")


    def _create_schema(self) -> Schema:
        return self.Schema(
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
            func=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return await self._create_room(schema)


    async def _create_room(self, schema: Schema) -> Any:
        client = await self._get_client()

        options = CreateRoomOptions(title=schema.title)

        room, response = client.files.create_room(options)
        if isinstance(response, ErrorResponse):
            raise response.exception

        return room
