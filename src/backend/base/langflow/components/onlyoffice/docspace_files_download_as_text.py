from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace import (
    AuthTextInput,
    Component,
    DataOutput,
    ErrorResponse,
    FileIdInput,
    Syncer,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.schema import Data


class OnlyofficeDocspaceDownloadAsText(Component):
    display_name = "Download As Text"
    description = "Download a file from the ONLYOFFICE DocSpace as text."
    name = "OnlyofficeDocspaceDownloadAsText"


    inputs = [
        AuthTextInput(),
        FileIdInput(info="The ID of the file to download as text."),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        file_id: int = Field(..., description="The ID of the file to download as text.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            file_id=self.file_id,
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        text = await self._download_as_text(schema)
        return Data(data={"text": text})


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="onlyoffice_docspace_download_as_text",
            description="Download a file from ONLYOFFICE DocSpace as text.",
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    async def _tool_func(self, **kwargs) -> dict:
        schema = self.Schema(**kwargs)
        text = await self._download_as_text(schema)
        return {"text": text}


    async def _download_as_text(self, schema: Schema) -> str:
        client = await self._get_client()
        syncer = Syncer(client.files.list_operations)

        result, response = client.files.get_file(schema.file_id)
        if isinstance(response, ErrorResponse):
            raise response.exception

        file_type = result["fileType"]
        ext = self._get_ext(file_type)
        options = {"fileIds": [{"key": schema.file_id, "value": ext}]}

        result = syncer.do(client.files.bulk_download, options)

        request = client.create_request("GET", result[0].url)
        request.headers["Accept"] = "text/plain"

        with client.opener.open(request) as response:
            content = response.read()

        return content.decode("utf-8")


    def _get_ext(self, file_type: str) -> str:
        if file_type in ("Spreadsheet", 5):
            return ".csv"

        if file_type in ("Presentation", 6):
            return ".txt"

        if file_type in ("Document", 7):
            return ".txt"

        if file_type in ("Pdf", 10):
            return ".txt"

        msg = f"Unsupported file type: {file_type}"
        raise ValueError(msg)
