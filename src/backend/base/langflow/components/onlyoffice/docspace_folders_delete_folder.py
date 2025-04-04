from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace import (
    AuthTextInput,
    Component,
    DataOutput,
    DeleteFileOptions,
    FolderIdInput,
    Syncer,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.schema import Data


class OnlyofficeDocspaceDeleteFolder(Component):
    display_name = "Delete Folder"
    description = "Delete a folder from ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceDeleteFolder"


    inputs = [
        AuthTextInput(),
        FolderIdInput(info="The ID of the folder to delete."),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
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
        syncer = Syncer(client.files.list_operations)
        options = DeleteFileOptions(DeleteAfter=False, immediately=False)
        operations = syncer.do(client.files.delete_folder, schema.folder_id, options)
        return operations[0].model_dump(exclude_none=True, by_alias=True)
