from typing import Any
import time

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace.client import ArchiveRoomOptions, Client, ErrorResponse
from langflow.base.onlyoffice.docspace.component import Component
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput, SecretStrInput
from langflow.io import Output
from langflow.schema import Data
from langflow.template import Output


class OnlyofficeDocspaceArchiveRoom(Component):
    display_name = "Archive Room"
    description = "Archive a room in ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceArchiveRoom"


    inputs = [
        SecretStrInput(
            name="auth_text",
            display_name="Text from Basic Authentication",
            info="Text output from the Basic Authentication component.",
            advanced=True,
        ),
        MessageTextInput(
            name="room_id",
            display_name="Room ID",
            info="The ID of the room to archive.",
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
        room_id: int = Field(..., description="The ID of the room to archive.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            room_id=self.room_id,
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._archive_room(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_archive_room",
            description="Archive a room in ONLYOFFICE DocSpace.",
            func=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return await self._archive_room(schema)


    async def _archive_room(self, schema: Schema) -> Any:
        client = await self._get_client()

        options = ArchiveRoomOptions(DeleteAfter=True)

        result, response = client.files.archive_room(schema.room_id, options)
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
