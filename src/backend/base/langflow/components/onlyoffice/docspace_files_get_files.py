import json
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


class OnlyofficeDocspaceGetFiles(Component):
    display_name = "Get Files"
    description = "Get files from ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceGetFiles"


    inputs = [
        SecretStrInput(
            name="auth_text",
            display_name="Text from Basic Authentication",
            info="Text output from the Basic Authentication component.",
            advanced=True,
        ),
        MessageTextInput(
            name="file_ids",
            display_name="File IDs",
            info="The list of file IDs to get in JSON format.",
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
        file_ids: list[int] = Field(..., description="The list of file IDs to get.")


    def _create_schema(self) -> Schema:
        file_ids: list[int] | None = None
        if self.file_ids:
            file_ids = json.loads(self.file_ids)

        return self.Schema(
            file_ids=file_ids,
        )


    async def build_data(self) -> list[Data]:
        schema = self._create_schema()

        result: list[Data] = []
        for data in await self._get_files(schema):
            result.append(Data(data=data))

        return result


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_get_files",
            description="Get files from ONLYOFFICE DocSpace.",
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return await self._get_files(schema)


    async def _get_files(self, schema: Schema) -> list[Any]:
        client = await self._get_client()

        ls: list[Any] = []
        errs: list[Exception] = []

        for file_id in schema.file_ids:
            result, response = client.files.get_file(file_id)
            if isinstance(response, ErrorResponse):
                errs.append(response.exception)
            else:
                ls.append(result)

        if errs:
            raise ExceptionGroup("Multiple errors while getting files", errs)

        return ls
