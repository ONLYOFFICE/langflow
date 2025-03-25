from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel

from langflow.base.onlyoffice.docspace.client import ErrorResponse
from langflow.base.onlyoffice.docspace.component import Component
from langflow.field_typing import Tool
from langflow.inputs import SecretStrInput
from langflow.io import Output
from langflow.schema import Data
from langflow.template import Output


class OnlyofficeDocspaceListMy(Component):
    display_name = "List 'My Documents'"
    description = "List folders and files from ONLYOFFICE DocSpace 'My Documents' section."
    name = "OnlyofficeDocspaceListDocuments"


    inputs = [
        SecretStrInput(
            name="auth_text",
            display_name="Text from Basic Authentication",
            info="Text output from the Basic Authentication component.",
            advanced=True,
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
        pass


    def build_data(self) -> Data:
        data = self._list_my()
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_list_my",
            description="List folders and files from ONLYOFFICE DocSpace 'My Documents' section.",
            coroutine=self._list_my,
            args_schema=self.Schema,
        )


    async def _list_my(self) -> Any:
        client = await self._get_client()

        result, response = client.files.list_my()
        if isinstance(response, ErrorResponse):
            raise response.exception

        return result
