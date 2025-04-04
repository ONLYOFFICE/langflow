from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace import (
    ArchiveRoomOptions,
    AuthTextInput,
    Component,
    DataOutput,
    RoomIdInput,
    Syncer,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.schema import Data


class OnlyofficeDocspaceArchiveRoom(Component):
    display_name = "Archive Room"
    description = "Archive a room in ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceArchiveRoom"


    inputs = [
        AuthTextInput(),
        RoomIdInput(info="The ID of the room to archive."),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
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
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return await self._archive_room(schema)


    async def _archive_room(self, schema: Schema) -> Any:
        client = await self._get_client()
        syncer = Syncer(client.files.list_operations)
        options = ArchiveRoomOptions(DeleteAfter=False)
        operation = syncer.do(client.files.archive_room, schema.room_id, options)
        return operation.model_dump(exclude_none=True, by_alias=True)
