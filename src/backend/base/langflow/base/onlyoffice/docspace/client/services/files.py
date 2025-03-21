from __future__ import annotations
from typing import Any, Tuple
from pydantic import BaseModel, Field
from ..base import Response, Service


class CreateFolderOptions(BaseModel):
    title: str | None = Field(None)


class DeleteFileOptions(BaseModel):
    delete_after: bool | None = Field(None, alias="DeleteAfter")
    immediately: bool | None = Field(None)


class UpdateFileOptions(BaseModel):
    title: str | None = Field(None)


class CreateRoomOptions(BaseModel):
    title: str | None = Field(None)


class UpdateRoomOptions(BaseModel):
    title: str | None = Field(None)


class ArchiveRoomOptions(BaseModel):
    delete_after: bool | None = Field(None, alias="DeleteAfter")


class FilesService(Service):
    def list_my(self) -> Tuple[Any, Response]:
        return self._client.get(
            "api/2.0/files/my",
        )


    def list_operations(self) -> Tuple[Any, Response]:
        return self._client.get(
            "api/2.0/files/fileops",
        )


    def bulk_download(self, options: dict) -> Tuple[Any, Response]:
        return self._client.put(
            "api/2.0/files/fileops/bulkdownload",
            body=options,
        )


    def get_folder(self, folder_id: int) -> Tuple[Any, Response]:
        return self._client.get(
            f"api/2.0/files/{folder_id}",
        )


    def create_folder(self, parent_id: int, options: CreateFolderOptions) -> Tuple[Any, Response]:
        return self._client.post(
            f"api/2.0/files/folder/{parent_id}",
            body=options.model_dump(),
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
            body=options.model_dump(),
        )


    def update_file(self, file_id: int, options: UpdateFileOptions) -> Tuple[Any, Response]:
        return self._client.put(
            f"api/2.0/files/file/{file_id}",
            body=options.model_dump(),
        )


    def get_file_download_link(self, file_id: int) -> Tuple[Any, Response]:
        return self._client.get(
            f"api/2.0/files/file/{file_id}/presigneduri",
        )


    def create_room(self, options: CreateRoomOptions) -> Tuple[Any, Response]:
        return self._client.post(
            "api/2.0/files/rooms",
            body=options.model_dump(),
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
            body=options.model_dump(),
        )


    def archive_room(self, room_id: int, options: ArchiveRoomOptions) -> Tuple[Any, Response]:
        return self._client.put(
            f"api/2.0/files/rooms/{room_id}/archive",
            body=options.model_dump(),
        )
