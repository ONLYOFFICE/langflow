from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace.client import ErrorResponse
from langflow.base.onlyoffice.docspace.component import Component
from langflow.base.onlyoffice.docspace.inputs import filters_inputs
from langflow.base.onlyoffice.docspace.schemas import FiltersSchema
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput, SecretStrInput
from langflow.io import Output
from langflow.schema import Data
from langflow.template import Output


class OnlyofficeDocspaceGetFolder(Component):
    display_name = "Get Folder"
    description = "Get a folder from ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceGetFolder"


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
            info="The ID of the folder to get.",
        ),
        *filters_inputs(),
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
        folder_id: int = Field(..., description="The ID of the folder to get.")
        filters: FiltersSchema = Field(FiltersSchema(), description="Filters to apply to the request.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            folder_id=self.folder_id,
            filters=FiltersSchema.from_component(self),
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
            schema.filters,
        )

        if isinstance(response, ErrorResponse):
            raise response.exception

        return result
