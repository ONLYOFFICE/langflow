from urllib.request import Request

from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace import (
    AuthTextInput,
    Component,
    ErrorResponse,
    FileIdInput,
)
from langflow.inputs import MessageTextInput
from langflow.schema import Message
from langflow.template import Output


class OnlyofficeDocspaceDownloadFile(Component):
    display_name = "Download File"
    description = "Download a file from ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceDownloadFile"


    inputs = [
        AuthTextInput(),
        FileIdInput(info="The ID of the file to download."),
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
            display_name="Text",
            name="api_build_text",
            method="build_text",
        ),
    ]


    class Schema(BaseModel):
        file_id: int = Field(..., description="The ID of the file to download.")
        chunk_size: int = Field(1024 * 1024, description="The size of each chunk to download.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            file_id=self.file_id,
            chunk_size=self.chunk_size,
        )


    def build_text(self) -> Message:
        schema = self._create_schema()
        text = self._download_file(schema)
        return Message(text=text)


    async def _download_file(self, schema: Schema):
        client = await self._get_client()

        url, response = client.files.get_file_download_link(schema.file_id)
        if isinstance(response, ErrorResponse):
            raise response.exception

        opener = client.opener

        try:
            req = Request(url, method="HEAD")  # noqa: S310
            with opener.open(req) as res:
                total_size = int(res.headers.get("Content-Length", 0))
        except:  # noqa: E722
            req = Request(url, method="GET")  # noqa: S310
            with opener.open(req) as res:
                total_size = int(res.headers.get("Content-Length", 0))

        downloaded = 0

        while downloaded < total_size:
            end = min(downloaded + schema.chunk_size - 1, total_size - 1)
            req = Request(url, method="GET", headers={"Range": f"bytes={downloaded}-{end}"})  # noqa: S310

            with opener.open(req) as res:
                chunk = res.read()

                actual_size = len(chunk)
                downloaded += actual_size

                yield Message(content=chunk.decode("utf-8"))

                if actual_size < (end - downloaded + 1) and actual_size > 0:
                    break
