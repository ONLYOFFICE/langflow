from typing import Any
import time

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace.client import Client, ErrorResponse
from langflow.base.onlyoffice.docspace.component import Component
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput, SecretStrInput
from langflow.io import Output
from langflow.schema import Data
from langflow.template import Output


class OnlyofficeDocspaceDownloadAsText(Component):
    display_name = "Download As Text"
    description = "Download a file from the ONLYOFFICE DocSpace as text."
    documentation = "https://api.onlyoffice.com/openapi/docspace/api-backend/usage-api/bulk-download/"
    name = "OnlyofficeDocspaceDownloadAsText"


    inputs = [
        SecretStrInput(
            name="auth_text",
            display_name="Text from Basic Authentication",
            info="Text output from the Basic Authentication component.",
            advanced=True,
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


    async def build_data(self) -> Data:
        schema = self._create_schema()
        text = await self._download_as_text(schema)
        return Data(data={"text": text})


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_download_as_text",
            description="Download a file from ONLYOFFICE DocSpace as text.",
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> dict:
        schema = self.Schema(**kwargs)
        text = await self._download_as_text(schema)
        return {"text": text}


    async def _download_as_text(self, schema: Schema) -> str:
        client = await self._get_client()

        result, response = client.files.get_file(schema.file_id)
        if isinstance(response, ErrorResponse):
            raise response.exception

        type = result["fileType"]
        ext = self._get_ext(type)
        options = {"fileIds": [{"key": schema.file_id, "value": ext}]}

        result, response = client.files.bulk_download(options)
        if isinstance(response, ErrorResponse):
            raise response.exception

        id = result[0]["id"]
        result = self._wait_operation(client, id)
        url = ""
        for item in result:
            if item["id"] == id:
                url = item["url"]
                break

        request = client.create_request("GET", url)
        request.headers["Accept"] = "text/plain"

        with client.opener.open(request) as response:
            content = response.read()

        return content.decode("utf-8")


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


    def _wait_operation(self, client: Client, id: int) -> Any:
        finished = False
        body = {}

        delay = 100 / 1000
        limit = 100

        while limit > 0:
            body, response = client.files.list_operations()
            if isinstance(response, ErrorResponse):
                raise response.exception

            for item in body:
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
