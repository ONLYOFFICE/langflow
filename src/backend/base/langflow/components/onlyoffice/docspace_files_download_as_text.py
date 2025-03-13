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


class OnlyofficeDocspaceDownloadAsText(ComponentWithCache):
    display_name = "Download As Text"
    description = "Download a file from the ONLYOFFICE DocSpace as text."
    documentation = "https://api.onlyoffice.com/openapi/docspace/api-backend/usage-api/bulk-download/"
    icon = "onlyoffice"
    name = "OnlyofficeDocspaceDownloadAsText"


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
            info="The ID of the file to download as text.",
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
        file_id: int = Field(..., description="The ID of the file to download as text.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            file_id=self.file_id,
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        body = self._download_as_text(schema)
        return Data(data=body)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_download_as_text",
            description="Download a file from ONLYOFFICE DocSpace as text.",
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> dict:
        schema = self.Schema(**kwargs)
        return self._download_as_text(schema)


    def _download_as_text(self, schema: Schema) -> str:
        body = self._get_file(schema)
        type = body["response"]["fileType"]
        ext = self._get_ext(type)
        body = self._start_downloading(schema, ext)
        id = body["response"][0]["id"]
        operations = self._wait_operation(id)
        url = ""
        for item in operations["response"]:
            if item["id"] == id:
                url = item["url"]
                break
        return self._download_file(url)


    def _get_file(self, schema: Schema) -> dict:
        data = json.loads(self.auth_text)
        url = urljoin(data["base_url"], f"api/2.0/files/file/{schema.file_id}")
        headers = {
            "Accept": "application/json",
            "Authorization": f"{data["token"]}",
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


    def _get_ext(self, type: str) -> str:
        if type == "Spreadsheet" or type == 5:
            return ".csv"
        elif type == "Presentation" or type == 6:
            return ".txt"
        elif type == "Document" or type == 7:
            return ".txt"
        elif type == "Pdf" or type == 10:
            return ".txt"
        else:
            raise ValueError(f"Unsupported file type: {type}")


    def _start_downloading(self, schema: Schema, ext: str) -> dict:
        data = json.loads(self.auth_text)
        url = urljoin(data["base_url"], "api/2.0/files/fileops/bulkdownload")
        headers = {
            "Accept": "application/json",
            "Authorization": f"{data["token"]}",
        }
        body = {
            "fileIds": [
                {
                    "key": schema.file_id,
                    "value": ext,
                },
            ],
        }
        response = requests.put(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()


    def _download_file(self, url: str) -> str:
        data = json.loads(self.auth_text)
        headers = {
            "Accept": "text/plain",
            "Authorization": f"{data["token"]}",
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text


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
