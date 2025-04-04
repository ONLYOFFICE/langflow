from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace import (
    AuthTextInput,
    Component,
    DataOutput,
    ErrorResponse,
    FiltersMixin,
    FiltersSchema,
    FolderIdInput,
    ToolOutput,
    filters_inputs,
)
from langflow.field_typing import Tool
from langflow.schema import Data


class OnlyofficeDocspaceGetFolder(Component, FiltersMixin):
    display_name = "Get Folder"
    description = "Get a folder from ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceGetFolder"


    inputs = [
        AuthTextInput(),
        FolderIdInput(info="The ID of the folder to get."),
        *filters_inputs(),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        folder_id: int = Field(..., description="The ID of the folder to get.")
        filters: FiltersSchema = Field(FiltersSchema(), description="Filters to apply to the request.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            folder_id=self.folder_id,
            filters=self.filters,
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._get_folder(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_get_folder",
            description="Get a folder from ONLYOFFICE DocSpace.",
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return await self._get_folder(schema)


    async def _get_folder(self, schema: Schema) -> Any:
        client = await self._get_client()

        result, response = client.files.get_folder(
            schema.folder_id,
            schema.filters.to_filters(),
        )

        if isinstance(response, ErrorResponse):
            raise response.exception

        return result
