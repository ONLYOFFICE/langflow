from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace.client import ErrorResponse
from langflow.base.onlyoffice.docspace.component import Component
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput, SecretStrInput
from langflow.io import Output
from langflow.schema import Data
from langflow.template import Output


class OnlyofficeDocspaceListSubfolders(Component):
    display_name = "List Subfolders"
    description = "List subfolders in ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceListSubfolders"


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
            info="The ID of the folder to list subfolders for.",
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
        folder_id: int = Field(..., description="The ID of the folder to list subfolders for.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            folder_id=self.folder_id,
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._list_subfolders(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_list_subfolders",
            description="List subfolders in ONLYOFFICE DocSpace.",
            func=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return await self._get_room(schema)


    async def _list_subfolders(self, schema: Schema) -> Any:
        client = await self._get_client()

        result, response = client.files.get_subfolders(schema.folder_id)
        if isinstance(response, ErrorResponse):
            raise Exception(response.message)

        return result
