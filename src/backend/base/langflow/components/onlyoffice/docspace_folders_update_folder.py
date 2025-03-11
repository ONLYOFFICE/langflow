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


class OnlyofficeDocspaceUpdateFolder(ComponentWithCache):
    display_name = "Update Folder"
    description = "Update a folder in ONLYOFFICE DocSpace."
    icon = "onlyoffice"
    name = "OnlyofficeDocspaceUpdateFolder"


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
            name="folder_id",
            display_name="Folder ID",
            info="The ID of the folder to update.",
        ),
        MessageTextInput(
            name="title",
            display_name="Title",
            info="The new title of the folder.",
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
        folder_id: int = Field(..., description="The ID of the folder to update.")
        title: str = Field(..., description="The new title of the folder.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            folder_id=self.folder_id,
            title=self.title,
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._update_folder(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_update_folder",
            description="Update a folder in ONLYOFFICE DocSpace.",
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> dict:
        schema = self.Schema(**kwargs)
        return self._update_folder(schema)


    def _update_folder(self, schema: Schema) -> dict:
        data = json.loads(self.auth_text)
        url = urljoin(data["base_url"], f"api/2.0/files/{schema.folder_id}")
        headers = {
            "Accept": "application/json",
            "Authorization": f"{data["token"]}",
        }
        body = {
            "title": schema.title,
        }
        response = requests.put(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()
