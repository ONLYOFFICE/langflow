from typing import Any
import time

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace.client import Client, DeleteFileOptions, ErrorResponse
from langflow.base.onlyoffice.docspace.component import Component
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput, SecretStrInput
from langflow.io import Output
from langflow.schema import Data
from langflow.template import Output


class OnlyofficeDocspaceDeleteFile(Component):
    display_name = "Delete File"
    description = "Delete a file from ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceDeleteFile"


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


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._delete_file(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_delete_file",
            description="Delete a file from ONLYOFFICE DocSpace.",
            func=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return await self._delete_file(schema)


    async def _delete_file(self, schema: Schema) -> Any:
        client = await self._get_client()

        options = DeleteFileOptions(DeleteAfter=True, immediately=True)

        result, response = client.files.delete_file(schema.file_id, options)
        if isinstance(response, ErrorResponse):
            raise response.exception

        return self._wait_operation(client, result["id"])


    def _wait_operation(self, client: Client, id: int) -> dict:
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
