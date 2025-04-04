from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace import (
    INPUT_FORMAT_FILE_IDS,
    INPUT_FORMAT_FOLDER_IDS,
    AuthTextInput,
    Component,
    DataOutput,
    DestFolderIdInput,
    FileIdsInput,
    FileIdsMixin,
    FolderIdsInput,
    FolderIdsMixin,
    IdSeparatorInput,
    IdSeparatorMixin,
    MoveOptions,
    Syncer,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Copy files and folders in ONLYOFFICE DocSpace."
DESCRIPTION_FOLDER_IDS = "The list of folder IDs to copy."
DESCRIPTION_FILE_IDS = "The list of file IDs to copy."
DESCRIPTION_DEST_FOLDER_ID = "The ID of the destination folder to copy the files and folders to."


class OnlyofficeDocspaceCopy(
    Component,
    IdSeparatorMixin,
    FolderIdsMixin,
    FileIdsMixin,
):
    display_name = "Copy"
    description = DESCRIPTION_COMPONENT
    name = "OnlyofficeDocspaceCopy"


    inputs = [
        AuthTextInput(),
        FolderIdsInput(info=f"{DESCRIPTION_FOLDER_IDS} {INPUT_FORMAT_FOLDER_IDS}"),
        FileIdsInput(info=f"{DESCRIPTION_FILE_IDS} {INPUT_FORMAT_FILE_IDS}"),
        DestFolderIdInput(info=DESCRIPTION_DEST_FOLDER_ID),
        IdSeparatorInput(),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        folder_ids: list[int | str] | None = Field(None, description=DESCRIPTION_FOLDER_IDS)
        file_ids: list[int | str] | None = Field(None, description=DESCRIPTION_FILE_IDS)
        dest_folder_id: int | str | None = Field(None, description=DESCRIPTION_DEST_FOLDER_ID)


    def _create_schema(self) -> Schema:
        return self.Schema(
            folder_ids=self.folder_ids,
            file_ids=self.file_ids,
            dest_folder_id=self.dest_folder_id,
        )


    async def build_data(self) -> list[Data]:
        schema = self._create_schema()
        return [Data(data=data) for data in await self._copy(schema)]


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_copy",
            description=DESCRIPTION_COMPONENT,
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return await self._copy(schema)


    async def _copy(self, schema: Schema) -> list[Any]:
        client = await self._get_client()
        syncer = Syncer(client.files.list_operations)
        options = MoveOptions(
            folderIds=schema.folder_ids,
            fileIds=schema.file_ids,
            destFolderId=schema.dest_folder_id,
        )
        operations = syncer.do(client.files.copy, options)
        return [operation.model_dump(exclude_none=True, by_alias=True) \
            for operation in operations]
