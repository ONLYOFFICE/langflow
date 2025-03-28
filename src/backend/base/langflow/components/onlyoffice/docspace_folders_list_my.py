from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel

from langflow.base.onlyoffice.docspace import (
    AuthTextInput,
    Component,
    DataOutput,
    ErrorResponse,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.schema import Data


class OnlyofficeDocspaceListMy(Component):
    display_name = "List 'My Documents'"
    description = "List folders and files from ONLYOFFICE DocSpace 'My Documents' section."
    name = "OnlyofficeDocspaceListDocuments"


    inputs = [
        AuthTextInput(),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        pass


    async def build_data(self) -> Data:
        data = await self._list_my()
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
