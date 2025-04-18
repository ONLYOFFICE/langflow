from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace import (
    AuthTextInput,
    Component,
    CreateFolderOptions,
    DataOutput,
    ErrorResponse,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data


class OnlyofficeDocspaceCreateFolder(Component):
    display_name = "Create Folder"
    description = "Create a folder in ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceCreateFolder"


    inputs = [
        AuthTextInput(),
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
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        room_id_or_folder_id: int = Field(..., description="The ID of the room or folder to create the folder in.")
        title: str = Field(..., description="The title of the folder.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            room_id_or_folder_id=self.room_id_or_folder_id,
            title=self.title,
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._create_folder(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_create_folder",
            description="Create a folder in ONLYOFFICE DocSpace.",
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return await self._create_folder(schema)


    async def _create_folder(self, schema: Schema) -> Any:
        client = await self._get_client()

        options = CreateFolderOptions(title=schema.title)

        result, response = client.files.create_folder(schema.room_id_or_folder_id, options)
        if isinstance(response, ErrorResponse):
            raise response.exception

        return result
