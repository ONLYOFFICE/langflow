import math
from datetime import datetime, timezone
from typing import Any

from langflow.base.onlyoffice.docspace import (
    AuthTextInput,
    Component,
    CreateSessionOptions,
    DataOutput,
    ErrorResponse,
    FolderIdInput,
    UploadChunkOptions,
)
from langflow.inputs import MessageTextInput
from langflow.schema import Data

MAX_CHUNK_SIZE = 1024 * 1024 * 10 # 10mb


class OnlyofficeDocspaceUploadFile(Component):
    display_name = "Upload File"
    description = "Upload a file to ONLYOFFICE DocSpace."
    name = "OnlyofficeDocspaceUploadFile"


    inputs = [
        AuthTextInput(),
        FolderIdInput(info="The ID of the folder to upload the file to."),
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
        DataOutput(),
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
            session_id = session_result["data"]["id"]
            start = index * MAX_CHUNK_SIZE
            end = (index + 1) * MAX_CHUNK_SIZE
            chunk = self.content[start:end].encode("utf-8")

            upload_options = UploadChunkOptions(
                filename=self.filename,
                chunk=chunk,
            )

            upload_result, response = client.files.upload_chunk(session_id, upload_options)
            if isinstance(response, ErrorResponse):
                raise response.exception

        return upload_result
