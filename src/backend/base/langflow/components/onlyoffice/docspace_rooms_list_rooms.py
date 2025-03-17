import json

from langchain.tools import StructuredTool
from pydantic import BaseModel

from langflow.base.onlyoffice.docspace.client import ErrorResponse, Client
from langflow.custom.custom_component.component_with_cache import ComponentWithCache
from langflow.field_typing import Tool
from langflow.inputs import SecretStrInput
from langflow.io import Output
from langflow.schema import Data
from langflow.template import Output


class OnlyofficeDocspaceListRooms(ComponentWithCache):
    display_name = "List Rooms"
    description = "List rooms in ONLYOFFICE DocSpace."
    icon = "onlyoffice"
    name = "OnlyofficeDocspaceListRooms"


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
        pass


    def build_data(self) -> Data:
        data = self._list_rooms()
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_list_rooms",
            description="List rooms in ONLYOFFICE DocSpace.",
            func=self._list_rooms,
            args_schema=self.Schema,
        )


    def _list_rooms(self) -> dict:
        data = json.loads(self.auth_text)

        client = Client()
        client.base_url = data["base_url"]
        client = client.with_auth_token(data["token"])

        list, response = client.files.list_rooms()
        if isinstance(response, ErrorResponse):
            raise response.exception

        return list
