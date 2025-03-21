from urllib.request import Request

from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace.client import ErrorResponse
from langflow.base.onlyoffice.docspace.component import Component
from langflow.inputs import MessageTextInput, SecretStrInput
from langflow.io import Output
from langflow.schema import Message
from langflow.template import Output


class OnlyofficeDocspaceDownloadFile(Component):
    display_name = "Download File"
    description = "Download a file from ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceDownloadFile"


    inputs = [
        SecretStrInput(
            name="auth_text",
            display_name="Text from Basic Authentication",
            info="Text output from the Basic Authentication component.",
            advanced=True,
        ),
        MessageTextInput(
            name="file_id",
            display_name="File ID",
            info="The ID of the file to download.",
        ),
        MessageTextInput(
            name="chunk_size",
            display_name="Chunk Size",
            info="The size of each chunk to download.",
            value="1048576", # 1mb
            advanced=True,
        ),
    ]


    outputs = [
        Output(
            display_name="Content",
            name="api_build_content",
            method="build_content",
        ),
        Output(
            display_name="Text",
            name="api_build_text",
            method="build_text",
            hidden=True,
        ),
    ]


    class Schema(BaseModel):
        file_id: int = Field(..., description="The ID of the file to download.")
        chunk_size: int = Field(1024 * 1024, description="The size of each chunk to download.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            file_id=self.file_id,
        )


    async def build_content(self) -> Message:
        schema = self._create_schema()
        chunk = await self._download_file(schema)
        return Message(content=chunk)


    async def build_text(self) -> Message:
        schema = self._create_schema()
        chunk = await self._download_file(schema)
        text = chunk.decode("utf-8")
        return Message(text=text)


    async def _download_file(self, schema: Schema):
        client = await self._get_client()

        url, response = client.files.get_file_download_link(schema.file_id)
        if isinstance(response, ErrorResponse):
            raise response.exception

        opener = client.opener

        try:
            req = Request(url, method="HEAD")
            with opener.open(req) as res:
                total_size = int(res.headers.get("Content-Length", 0))
        except:
            req = Request(url, method="GET")
            with opener.open(req) as res:
                total_size = int(res.headers.get("Content-Length", 0))

        downloaded = 0

        while downloaded < total_size:
            end = min(downloaded + schema.chunk_size - 1, total_size - 1)
            req = Request(url, method="GET", headers={"Range": f"bytes={downloaded}-{end}"})

            with opener.open(req) as res:
                chunk = res.read()

                actual_size = len(chunk)
                downloaded += actual_size

                yield chunk

                if actual_size < (end - downloaded + 1) and actual_size > 0:
                    break
