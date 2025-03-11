import json
import time
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


class OnlyofficeDocspaceDeleteFile(ComponentWithCache):
    display_name = "Delete File"
    description = "Delete a file from ONLYOFFICE DocSpace."
    icon = "onlyoffice"
    name = "OnlyofficeDocspaceDeleteFile"


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
            name="file_id",
            display_name="File ID",
            info="The ID of the file to delete.",
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
        file_id: int = Field(..., description="The ID of the file to delete.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            file_id=self.file_id,
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._delete_file(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_delete_file",
            description="Delete a file from ONLYOFFICE DocSpace.",
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> dict:
        schema = self.Schema(**kwargs)
        return self._delete_file(schema)


    def _delete_file(self, schema: Schema) -> dict:
        body = self._start_deleting_file(schema)
        id = body["response"]["id"]
        return self._wait_operation(id)


    def _start_deleting_file(self, schema: Schema) -> dict:
        data = json.loads(self.auth_text)
        url = urljoin(data["base_url"], f"api/2.0/files/file/{schema.file_id}")
        headers = {
            "Accept": "application/json",
            "Authorization": f"{data["token"]}",
        }
        body = {
            "deleteAfter": True,
            "immediately": True,
        }
        response = requests.delete(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()


    #
    # async
    #

    def _wait_operation(self, id: int) -> dict:
        finished = False
        body = {}

        delay = 100 / 1000
        limit = 100

        while limit > 0:
            body = self._list_operations()

            for item in body["response"]:
                if item["id"] == id and item["finished"]:
                    finished = True
                    break

            if finished:
                break

            limit -= 1
            time.sleep(delay)

        if not finished:
            raise ValueError(f"Operation {id} did not finish in time")

        return body


    def _list_operations(self) -> dict:
        data = json.loads(self.auth_text)
        url = urljoin(data["base_url"], "api/2.0/files/fileops")
        headers = {
            "Accept": "application/json",
            "Authorization": f"{data["token"]}",
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
