import json

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace.client import ErrorResponse, Client
from langflow.custom.custom_component.component_with_cache import ComponentWithCache
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput, SecretStrInput
from langflow.io import Output
from langflow.schema import Data
from langflow.template import Output


class OnlyofficeDocspaceGetRoom(ComponentWithCache):
    display_name = "Get Room"
    description = "Get a room from ONLYOFFICE DocSpace."
    icon = "onlyoffice"
    name = "OnlyofficeDocspaceGetRoom"


    inputs = [
        SecretStrInput(
            name="auth_text",
            display_name="Text from Basic Authentication",
            info="Text output from the Basic Authentication component.",
            value="""{
                "base_url": "",
                "token": ""
            }""",
        ),
        MessageTextInput(
            name="room_id",
            display_name="Room ID",
            info="The ID of the room to get.",
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
        room_id: int = Field(..., description="The ID of the room to get.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            room_id=self.room_id,
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._get_room(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_get_room",
            description="Get a room from ONLYOFFICE DocSpace.",
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> dict:
        schema = self.Schema(**kwargs)
        return self._get_room(schema)


    def _get_room(self, schema: Schema) -> dict:
        data = json.loads(self.auth_text)

        client = Client()
        client.base_url = data["base_url"]
        client = client.with_auth_token(data["token"])

        room, response = client.files.get_room(schema.room_id)
        if isinstance(response, ErrorResponse):
            raise response.exception

        return room
