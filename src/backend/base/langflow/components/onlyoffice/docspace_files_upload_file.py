from datetime import datetime, timezone
import math
from typing import Any

# from langchain.tools import StructuredTool
# from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace.client import CreateSessionOptions, ErrorResponse, UploadChunkOptions
from langflow.base.onlyoffice.docspace.component import Component
# from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput, SecretStrInput
from langflow.io import Output
from langflow.schema import Data
from langflow.template import Output


MAX_CHUNK_SIZE = 1024 * 1024 * 10 # 10mb


class OnlyofficeDocspaceUploadFile(Component):
    display_name = "Upload File"
    description = "Upload a file to ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceUploadFile"


    inputs = [
        SecretStrInput(
            name="auth_text",
            display_name="Text from Basic Authentication",
            info="Text output from the Basic Authentication component.",
            advanced=True,
        ),
        MessageTextInput(
            name="folder_id",
            display_name="Folder ID",
            info="The ID of the folder to upload the file to.",
        ),
        MessageTextInput(
            name="filename",
            display_name="Filename",
            info="The name of the file to upload.",
        ),
        MessageTextInput(
            name="content",
            display_name="Content",
            info="The content of the file to upload.",
        ),
    ]


    outputs = [
        Output(
            display_name="Data",
            name="api_build_data",
            method="build_data",
        ),
    ]


    async def build_data(self) -> Data:
        data = await self._upload_file()
        return Data(data=data)


    async def _upload_file(self) -> Any:
        client = await self._get_client()

        filesize = len(self.content)
        create_on = datetime.now(timezone.utc).isoformat()

        session_options = CreateSessionOptions(
            folderId=self.folder_id,
            FileName=self.filename,
            FileSize=filesize,
            CreateOn=create_on,
        )

        session_result, response = client.files.create_session(self.folder_id, session_options)
        if isinstance(response, ErrorResponse):
            raise response.exception

        chunks = math.ceil(filesize / MAX_CHUNK_SIZE)

        for index in range(chunks):
            id = session_result["data"]["id"]
            start = index * MAX_CHUNK_SIZE
            end = (index + 1) * MAX_CHUNK_SIZE
            chunk = self.content[start:end].encode("utf-8")

            upload_options = UploadChunkOptions(
                filename=self.filename,
                chunk=chunk,
            )

            upload_result, response = client.files.upload_chunk(id, upload_options)
            if isinstance(response, ErrorResponse):
                raise response.exception

        return upload_result
