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


class OnlyofficeDocspaceDeleteFolder(Component):
    display_name = "Delete Folder"
    description = "Delete a folder from ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceDeleteFolder"


    inputs = [
        SecretStrInput(
            name="auth_text",
            display_name="Text from Basic Authentication",
            info="Text output from the Basic Authentication component.",
            advanced=True,
        ),
        MessageTextInput(
            name="folder_id",
            display_name="Folder ID",
            info="The ID of the folder to delete.",
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
        folder_id: int = Field(..., description="The ID of the folder to delete.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            folder_id=self.folder_id,
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._delete_folder(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_delete_folder",
            description="Delete a folder from ONLYOFFICE DocSpace.",
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return await self._delete_folder(schema)


    async def _delete_folder(self, schema: Schema) -> Any:
        client = await self._get_client()

        result, response = client.files.delete_folder(schema.folder_id)
        if isinstance(response, ErrorResponse):
            raise response.exception

        return self._wait_operation(client, result["id"])


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
