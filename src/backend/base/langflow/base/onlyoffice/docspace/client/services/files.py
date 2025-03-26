from __future__ import annotations
from typing import Any, Literal, Tuple
from pydantic import BaseModel, Field
from ..base import Response, Service, SuccessResponse, encode_multipart_formdata

# https://github.com/ONLYOFFICE/onlyoffice-zapier/blob/v1.1.0/app/docspace/files/files.js#L126


RoomType = \
    Literal[
        "FillingFormsRoom",
        "EditingRoom",
        "CustomRoom",
        "PublicRoom",
        "VirtualDataRoom",
    ] | \
    Literal[
        1,
        2,
        5,
        6,
        8,
    ]


class Operation(BaseModel):
    id: str | None = Field(None)
    error: str | None = Field(None)
    finished: bool | None = Field(None)
    percents: int | None = Field(None)
    progress: int | None = Field(None)


class MoveOptions(BaseModel):
    folder_ids: list[int | str] | None = Field(None, alias="folderIds")
    file_ids: list[int | str] | None = Field(None, alias="fileIds")
    dest_folder_id: int | str | None = Field(None, alias="destFolderId")


class CreateSessionOptions(BaseModel):
    folder_id: int | None = Field(None, alias="folderId")
    file_name: str | None = Field(None, alias="FileName")
    file_size: int | None = Field(None, alias="FileSize")
    create_on: str | None = Field(None, alias="CreateOn")


class CreateFolderOptions(BaseModel):
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


class UploadChunkOptions(BaseModel):
    filename: str | None = Field(None)
    chunk: bytes | None = Field(None)


class FilesService(Service):
    def list_my(self) -> Tuple[Any, Response]:
        return self._client.get(
            "api/2.0/files/@my",
        )


    def list_operations(self) -> Tuple[list[Operation], Response]:
        payload, response = self._client.get(
            "api/2.0/files/fileops",
        )

        ls: list[Operation] = []
        if isinstance(response, SuccessResponse):
            for item in payload:
                ls.append(Operation.model_validate(item))

        return ls, response


    def bulk_download(self, options: dict) -> Tuple[Any, Response]:
        return self._client.put(
            "api/2.0/files/fileops/bulkdownload",
            body=options,
        )


    def move(self, options: MoveOptions) -> Tuple[list[Operation], Response]:
        payload, response = self._client.put(
            "api/2.0/files/fileops/move",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )

        ls: list[Operation] = []
        if isinstance(response, SuccessResponse):
            for item in payload:
                ls.append(Operation.model_validate(item))

        return ls, response


    def create_session(self, folder_id: int, options: CreateSessionOptions) -> Tuple[Any, Response]:
        return self._client.post(
            f"api/2.0/files/{folder_id}/upload/create_session",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


    def get_folder(self, folder_id: int) -> Tuple[Any, Response]:
        return self._client.get(
            f"api/2.0/files/{folder_id}",
        )


    def create_folder(self, parent_id: int, options: CreateFolderOptions) -> Tuple[Any, Response]:
        return self._client.post(
            f"api/2.0/files/folder/{parent_id}",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


    def delete_folder(self, folder_id: int) -> Tuple[Any, Response]:
        return self._client.delete(
            f"api/2.0/files/folder/{folder_id}",
        )


    def list_subfolders(self, folder_id: int) -> Tuple[Any, Response]:
        return self._client.get(
            f"api/2.0/files/{folder_id}/subfolders",
        )


    def get_file(self, file_id: int) -> Tuple[Any, Response]:
        return self._client.get(
            f"api/2.0/files/file/{file_id}",
        )


    def delete_file(self, file_id: int, options: DeleteFileOptions) -> Tuple[Any, Response]:
        return self._client.delete(
            f"api/2.0/files/file/{file_id}",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


    def update_file(self, file_id: int, options: UpdateFileOptions) -> Tuple[Any, Response]:
        return self._client.put(
            f"api/2.0/files/file/{file_id}",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


    def get_file_download_link(self, file_id: int) -> Tuple[Any, Response]:
        return self._client.get(
            f"api/2.0/files/file/{file_id}/presigneduri",
        )


    def create_room(self, options: CreateRoomOptions) -> Tuple[Any, Response]:
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


    def list_rooms(self) -> Tuple[Any, Response]:
        return self._client.get(
            "api/2.0/files/rooms",
        )


    def get_room(self, room_id: int) -> Tuple[Any, Response]:
        return self._client.get(
            f"api/2.0/files/rooms/{room_id}",
        )


    def update_room(self, room_id: int, options: UpdateRoomOptions) -> Tuple[Any, Response]:
        return self._client.put(
            f"api/2.0/files/rooms/{room_id}",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


    def archive_room(self, room_id: int, options: ArchiveRoomOptions) -> Tuple[Any, Response]:
        return self._client.put(
            f"api/2.0/files/rooms/{room_id}/archive",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


    def upload_chunk(self, session_id: int, options: UploadChunkOptions) -> Tuple[Any, Response]:
        url = self._client.create_url(f"ChunkedUploader.ashx?uid={session_id}")
        content_type, data = encode_multipart_formdata(options.filename, options.chunk)
        req = self._client.create_request("POST", url)
        req.headers["Content-Type"] = content_type
        req.data = data
        return self._client.send_request(req)
