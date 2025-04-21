from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace.client.base import (
    Filters,
    Response,
    Service,
    SuccessResponse,
    encode_multipart_formdata,
)

# https://github.com/ONLYOFFICE/onlyoffice-zapier/blob/v1.1.0/app/docspace/files/files.js#L126


RoomType = Literal[
    "FillingFormsRoom",
    "EditingRoom",
    "CustomRoom",
    "PublicRoom",
    "VirtualDataRoom",
    1,
    2,
    5,
    6,
    8,
]


InvitationAccess = Literal[
    "None",
    "ReadWrite",
    "Read",
    "Restrict",
    "Varies",
    "Review",
    "Comment",
    "FillForms",
    "CustomFilter",
    "RoomManager",
    "Editing",
    "ContentCreator",
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
]


class Operation(BaseModel):
    id: str | None = Field(None)
    error: str | None = Field(None)
    finished: bool | None = Field(None)
    percents: int | None = Field(None)
    progress: int | None = Field(None)
    url: str | None = Field(None)


class Invitation(BaseModel):
    email: str | None = Field(None)
    id: str | None = Field(None)
    access: InvitationAccess | None = Field(None)


class MoveOptions(BaseModel):
    folder_ids: list[int | str] | None = Field(None, alias="folderIds")
    file_ids: list[int | str] | None = Field(None, alias="fileIds")
    dest_folder_id: int | str | None = Field(None, alias="destFolderId")


class CreateSessionOptions(BaseModel):
    folder_id: int | None = Field(None, alias="folderId")
    file_name: str | None = Field(None, alias="FileName")
    file_size: int | None = Field(None, alias="FileSize")
    create_on: str | None = Field(None, alias="CreateOn")


class CreateFileOptions(BaseModel):
    title: str | None = Field(None)
    template_id: int | None = Field(None, alias="templateId")
    form_id: int | None = Field(None, alias="formId")
    enable_external_ext: bool | None = Field(None, alias="enableExternalExt")


class CreateFolderOptions(BaseModel):
    title: str | None = Field(None)


class UpdateFolderOptions(BaseModel):
    title: str | None = Field(None)


class DeleteFileOptions(BaseModel):
    delete_after: bool | None = Field(None, alias="DeleteAfter")
    immediately: bool | None = Field(None)


class UpdateFileOptions(BaseModel):
    title: str | None = Field(None)


class CreateRoomOptions(BaseModel):
    room_type: RoomType | None = Field(None, alias="roomType")
    title: str | None = Field(None)


class UpdateRoomOptions(BaseModel):
    title: str | None = Field(None)


class ArchiveRoomOptions(BaseModel):
    delete_after: bool | None = Field(None, alias="DeleteAfter")


class SetRoomAccessRightOptions(BaseModel):
    invitations: list[Invitation] | None = Field(None)
    notify: bool | None = Field(None)
    message: str | None = Field(None)
    culture: str | None = Field(None)


class UploadChunkOptions(BaseModel):
    filename: str | None = Field(None)
    chunk: bytes | None = Field(None)


class FilesService(Service):
    def list_my(self) -> tuple[Any, Response]:
        return self._client.get(
            "api/2.0/files/@my",
        )


    def list_operations(self) -> tuple[list[Operation], Response]:
        payload, response = self._client.get(
            "api/2.0/files/fileops",
        )

        ls = [Operation.model_validate(item) for item in payload] \
            if isinstance(response, SuccessResponse) else []

        return ls, response


    def bulk_download(self, options: dict) -> tuple[list[Operation], Response]:
        payload, response = self._client.put(
            "api/2.0/files/fileops/bulkdownload",
            body=options,
        )

        ls = [Operation.model_validate(item) for item in payload] \
            if isinstance(response, SuccessResponse) else []

        return ls, response


    def copy(self, options: MoveOptions) -> tuple[list[Operation], Response]:
        payload, response = self._client.put(
            "api/2.0/files/fileops/copy",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )

        ls = [Operation.model_validate(item) for item in payload] \
            if isinstance(response, SuccessResponse) else []

        return ls, response


    def move(self, options: MoveOptions) -> tuple[list[Operation], Response]:
        payload, response = self._client.put(
            "api/2.0/files/fileops/move",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )

        ls = [Operation.model_validate(item) for item in payload] \
            if isinstance(response, SuccessResponse) else []

        return ls, response


    def create_file(self, folder_id: int, options: CreateFileOptions) -> tuple[Any, Response]:
        return self._client.post(
            f"api/2.0/files/{folder_id}/file",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


    def create_session(self, folder_id: int, options: CreateSessionOptions) -> tuple[Any, Response]:
        return self._client.post(
            f"api/2.0/files/{folder_id}/upload/create_session",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


    def get_folder(self, folder_id: int, filters: Filters | None = None) -> tuple[Any, Response]:
        query: dict[str, Any] | None = None
        if filters:
            query = filters.model_dump(exclude_none=True, by_alias=True)

        return self._client.get(
            f"api/2.0/files/{folder_id}",
            query=query,
        )


    def create_folder(self, parent_id: int, options: CreateFolderOptions) -> tuple[Any, Response]:
        return self._client.post(
            f"api/2.0/files/folder/{parent_id}",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


    def update_folder(self, folder_id: int, options: UpdateFolderOptions) -> tuple[Any, Response]:
        return self._client.put(
            f"api/2.0/files/folder/{folder_id}",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


    def delete_folder(self, folder_id: int, options: DeleteFileOptions) -> tuple[list[Operation], Response]:
        payload, response = self._client.delete(
            f"api/2.0/files/folder/{folder_id}",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )

        ls = [Operation.model_validate(item) for item in payload] \
            if isinstance(response, SuccessResponse) else []

        return ls, response


    def list_subfolders(self, folder_id: int) -> tuple[list[Any], Response]:
        return self._client.get(
            f"api/2.0/files/{folder_id}/subfolders",
        )


    def get_file(self, file_id: int) -> tuple[Any, Response]:
        return self._client.get(
            f"api/2.0/files/file/{file_id}",
        )


    def delete_file(self, file_id: int, options: DeleteFileOptions) -> tuple[list[Operation], Response]:
        payload, response = self._client.delete(
            f"api/2.0/files/file/{file_id}",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )

        ls = [Operation.model_validate(item) for item in payload] \
            if isinstance(response, SuccessResponse) else []

        return ls, response


    def update_file(self, file_id: int, options: UpdateFileOptions) -> tuple[Any, Response]:
        return self._client.put(
            f"api/2.0/files/file/{file_id}",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


    def get_file_download_link(self, file_id: int) -> tuple[Any, Response]:
        return self._client.get(
            f"api/2.0/files/file/{file_id}/presigneduri",
        )


    def create_room(self, options: CreateRoomOptions) -> tuple[Any, Response]:
        # There is a bug on the DocSpace that does not allow using string cases
        # of the RoomType enum.

        room_type = options.room_type

        if room_type is not None and isinstance(room_type, str):
            if room_type == "FillingFormsRoom":
                room_type = 1
            elif room_type == "EditingRoom":
                room_type = 2
            elif room_type == "CustomRoom":
                room_type = 5
            elif room_type == "PublicRoom":
                room_type = 6
            elif room_type == "VirtualDataRoom":
                room_type = 8

        options = CreateRoomOptions(
            roomType=room_type,
            title=options.title,
        )

        return self._client.post(
            "api/2.0/files/rooms",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


    def list_rooms(self) -> tuple[Any, Response]:
        return self._client.get(
            "api/2.0/files/rooms",
        )


    def get_room(self, room_id: int) -> tuple[Any, Response]:
        return self._client.get(
            f"api/2.0/files/rooms/{room_id}",
        )


    def update_room(self, room_id: int, options: UpdateRoomOptions) -> tuple[Any, Response]:
        return self._client.put(
            f"api/2.0/files/rooms/{room_id}",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


    def archive_room(self, room_id: int, options: ArchiveRoomOptions) -> tuple[Operation, Response]:
        payload, response = self._client.put(
            f"api/2.0/files/rooms/{room_id}/archive",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )

        model = Operation.model_validate(payload) \
            if isinstance(response, SuccessResponse) else Operation()

        return model, response


    def set_room_access_right(self, room_id: int, options: SetRoomAccessRightOptions) -> tuple[Any, Response]:
        return self._client.put(
            f"api/2.0/files/rooms/{room_id}/share",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


    def upload_chunk(self, session_id: int, options: UploadChunkOptions) -> tuple[Any, Response]:
        url = self._client.create_url(f"ChunkedUploader.ashx?uid={session_id}")
        content_type, data = encode_multipart_formdata(options.filename, options.chunk)
        req = self._client.create_request("POST", url)
        req.headers["Content-Type"] = content_type
        req.data = data
        return self._client.send_request(req)
