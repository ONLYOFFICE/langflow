from typing import Any
import time

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace.client import ErrorResponse
from langflow.base.onlyoffice.docspace.component import Component
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput, SecretStrInput
from langflow.io import Output
from langflow.schema import Data
from langflow.template import Output


class OnlyofficeDocspaceWaitOperation(Component):
    display_name = "Wait Operation"
    description = "Wait for an operation to finish in ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceWaitOperation"


    inputs = [
        SecretStrInput(
            name="auth_text",
            display_name="Text from Basic Authentication",
            info="Text output from the Basic Authentication component.",
            advanced=True,
        ),
        MessageTextInput(
            name="operation_id",
            display_name="Operation ID",
            info="The ID of the operation to wait for.",
        ),
        MessageTextInput(
            name="delay",
            display_name="Delay",
            info="The delay between each check in seconds.",
            value="0.1",
            advanced=True,
        ),
        MessageTextInput(
            name="max_retries",
            display_name="Max Retries",
            info="The maximum number of retries.",
            value="100",
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
        operation_id: str = Field(..., description="The ID of the operation to wait for.")
        delay: float = Field(0.1, description="The delay between each check in seconds.")
        max_retries: int = Field(100, description="The maximum number of retries.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            operation_id=self.operation_id,
            delay=self.delay,
            max_retries=self.max_retries,
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._wait_operation(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_wait_operation",
            description="Wait for an operation to finish in ONLYOFFICE DocSpace.",
            func=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return await self._wait_operation(schema)


    async def _wait_operation(self, schema: Schema) -> Any:
        client = await self._get_client()

        finished = False
        body = {}

        retries = schema.max_retries

        while retries > 0:
            body, response = client.files.list_operations()
            if isinstance(response, ErrorResponse):
                raise response.exception

            for item in body:
                if item["id"] == schema.id and item["finished"]:
                    finished = True
                    break

            if finished:
                break

            retries -= 1
            time.sleep(schema.delay)

        if not finished:
            raise ValueError(f"Operation {schema.id} did not finish in time")

        return body
