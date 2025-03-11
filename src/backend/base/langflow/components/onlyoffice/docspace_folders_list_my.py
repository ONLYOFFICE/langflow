import json
from urllib.parse import urljoin

from langchain.tools import StructuredTool
from pydantic import BaseModel
import requests

from langflow.custom.custom_component.component_with_cache import ComponentWithCache
from langflow.field_typing import Tool
from langflow.inputs import SecretStrInput
from langflow.io import Output
from langflow.schema import Data
from langflow.template import Output


class OnlyofficeDocspaceListMy(ComponentWithCache):
    display_name = "List 'My Documents'"
    description = "List folders and files from ONLYOFFICE DocSpace 'My Documents' section."
    documentation = "https://api.onlyoffice.com/openapi/docspace/api-backend/usage-api/get-my-folder/"
    icon = "onlyoffice"
    name = "OnlyofficeDocspaceListDocuments"


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
        data = self._list_my()
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_list_my",
            description="List folders and files from ONLYOFFICE DocSpace 'My Documents' section.",
            func=self._list_my,
            args_schema=self.Schema,
        )


    def _list_my(self) -> dict:
        data = json.loads(self.auth_text)
        url = urljoin(data["base_url"], "api/2.0/files/@my")
        headers = {
            "Accept": "application/json",
            "Authorization": f"{data["token"]}",
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
