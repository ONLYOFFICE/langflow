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


class OnlyofficeDocspaceGetCurrentPortal(Component):
    display_name = "Get Current Portal"
    description = "Get the current portal from ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceGetCurrentPortal"


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
        data = await self._get_current_portal()
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_get_current_portal",
            description="Get the current portal from ONLYOFFICE DocSpace.",
            coroutine=self._get_current_portal,
            args_schema=self.Schema,
        )


    async def _get_current_portal(self) -> Any:
        client = await self._get_client()

        result, response = client.portal.get_current()
        if isinstance(response, ErrorResponse):
            raise response.exception

        return result
