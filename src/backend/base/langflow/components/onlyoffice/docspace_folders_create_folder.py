import json
from urllib.parse import urljoin

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
import requests

from langflow.custom.custom_component.component_with_cache import ComponentWithCache
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput, SecretStrInput
from langflow.io import Output
from langflow.schema import Data
from langflow.template import Output


class OnlyofficeDocspaceCreateFolder(ComponentWithCache):
    display_name = "Create Folder"
    description = "Create a folder in ONLYOFFICE DocSpace."
    icon = "onlyoffice"
    name = "OnlyofficeDocspaceCreateFolder"


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
            name="room_id_or_folder_id",
            display_name="Room ID or Folder ID",
            info="The ID of the room or folder to create the folder in.",
        ),
        MessageTextInput(
            name="title",
            display_name="Title",
            info="The title of the folder.",
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
        room_id_or_folder_id: int = Field(..., description="The ID of the room or folder to create the folder in.")
        title: str = Field(..., description="The title of the folder.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            room_id_or_folder_id=self.room_id_or_folder_id,
            title=self.title,
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._create_folder(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_create_folder",
            description="Create a folder in ONLYOFFICE DocSpace.",
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> dict:
        schema = self.Schema(**kwargs)
        return self._create_folder(schema)


    def _create_folder(self, schema: Schema) -> dict:
        data = json.loads(self.auth_text)
        url = urljoin(data["base_url"], f"api/2.0/files/folder/{schema.room_id_or_folder_id}")
        headers = {
            "Accept": "application/json",
            "Authorization": f"{data["token"]}",
        }
        body = {
            "title": schema.title,
        }
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()
