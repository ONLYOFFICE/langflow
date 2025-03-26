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


class OnlyofficeDocspaceGetCurrentPortal(Component):
    display_name = "Get Current Portal"
    description = "Get the current portal from ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceGetCurrentPortal"


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
