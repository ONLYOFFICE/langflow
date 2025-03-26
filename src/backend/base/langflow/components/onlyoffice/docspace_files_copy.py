import json
from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace.client import MoveOptions
from langflow.base.onlyoffice.docspace.component import Component
from langflow.base.onlyoffice.docspace.syncer import Syncer
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput, SecretStrInput
from langflow.io import Output
from langflow.schema import Data
from langflow.template import Output


class OnlyofficeDocspaceCopy(Component):
    display_name = "Copy"
    description = "Copy files and folders in ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceCopy"


    inputs = [
        SecretStrInput(
            name="auth_text",
            display_name="Text from Basic Authentication",
            info="Text output from the Basic Authentication component.",
            advanced=True,
        ),
        MessageTextInput(
            name="folder_ids",
            display_name="Folder IDs",
            info="The list of folder IDs to copy in JSON format.",
        ),
        MessageTextInput(
            name="file_ids",
            display_name="File IDs",
            info="The list of file IDs to copy in JSON format.",
        ),
        MessageTextInput(
            name="dest_folder_id",
            display_name="Destination Folder ID",
            info="The ID of the destination folder to copy the files and folders to.",
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
        folder_ids: list[int | str] | None = Field(None, description="The list of folder IDs to copy.")
        file_ids: list[int | str] | None = Field(None, description="The list of file IDs to copy.")
        dest_folder_id: int | str | None = Field(None, description="The ID of the destination folder to copy the files and folders to.")


    def _create_schema(self) -> Schema:
        folder_ids: list[int] | list[str] | None = None
        if self.folder_ids:
            folder_ids = json.loads(self.folder_ids)

        file_ids: list[int] | list[str] | None = None
        if self.file_ids:
            file_ids = json.loads(self.file_ids)

        return self.Schema(
            folder_ids=folder_ids,
            file_ids=file_ids,
            dest_folder_id=self.dest_folder_id,
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._copy(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_copy",
            description="Copy files and folders in ONLYOFFICE DocSpace.",
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )

    async def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return await self._copy(schema)


    async def _copy(self, schema: Schema) -> Any:
        client = await self._get_client()

        options = MoveOptions(
            folderIds=schema.folder_ids,
            fileIds=schema.file_ids,
            destFolderId=schema.dest_folder_id,
        )

        syncer = Syncer(
            client.files.list_operations,
            client.files.copy,
            options,
        )

        syncer.do()
