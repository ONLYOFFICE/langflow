from __future__ import annotations
from typing import Any, Tuple
from pydantic import BaseModel, Field
from ..base import Response, Service


class DeleteFileOptions(BaseModel):
    delete_after: bool | None = Field(None, alias="DeleteAfter")
    immediately: bool | None = Field(None)


class CreateRoomOptions(BaseModel):
    title: str | None = Field(None)


class FilesService(Service):
    def delete_file(self, file_id: int, options: DeleteFileOptions) -> Tuple[Any, Response]:
        return self._client.delete(
            f"api/2.0/files/file/{file_id}",
            body=options.model_dump(),
        )


    def get_file(self, file_id: int) -> Tuple[Any, Response]:
        return self._client.get(
            f"api/2.0/files/file/{file_id}",
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


    def get_room(self, room_id: int) -> Tuple[Any, Response]:
        return self._client.get(
            f"api/2.0/files/rooms/{room_id}",
        )


    def list_rooms(self) -> Tuple[Any, Response]:
        return self._client.get(
            "api/2.0/files/rooms",
        )
