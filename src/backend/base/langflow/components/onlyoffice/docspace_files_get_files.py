from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace import (
    INPUT_FORMAT_FILE_IDS,
    AuthTextInput,
    Component,
    DataOutput,
    ErrorResponse,
    FileIdsInput,
    FileIdsMixin,
    IdSeparatorInput,
    IdSeparatorMixin,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Get files from ONLYOFFICE DocSpace."
DESCRIPTION_FILE_IDS = "The list of file IDs to get."


class OnlyofficeDocspaceGetFiles(Component, IdSeparatorMixin, FileIdsMixin):
    display_name = "Get Files"
    description = DESCRIPTION_COMPONENT
    name = "OnlyofficeDocspaceGetFiles"


    inputs = [
        AuthTextInput(),
        FileIdsInput(info=f"{DESCRIPTION_FILE_IDS} {INPUT_FORMAT_FILE_IDS}"),
        IdSeparatorInput(),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        file_ids: list[int | str] = Field(..., description=DESCRIPTION_FILE_IDS)


    def _create_schema(self) -> Schema:
        return self.Schema(
            file_ids=self.file_ids,
        )


    async def build_data(self) -> list[Data]:
        schema = self._create_schema()
        return [Data(data=data) for data in await self._get_files(schema)]


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_get_files",
            description=DESCRIPTION_COMPONENT,
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
            msg = "Multiple errors while getting files"
            raise ExceptionGroup(msg, errs)

        return ls
