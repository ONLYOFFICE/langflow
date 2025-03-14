from __future__ import annotations
from typing import Any, Protocol
from http.client import HTTPResponse
from urllib.request import Request as HTTPRequest
from pydantic import BaseModel, Field

# https://github.com/ONLYOFFICE/DocSpace-server/blob/v3.0.4-server/common/ASC.Api.Core/Middleware/CommonApiResponse.cs/
# https://github.com/ONLYOFFICE/DocSpace-server/blob/v3.0.4-server/products/ASC.Files/Core/ApiModels/ResponseDto/UploadResultDto.cs/
# https://github.com/ONLYOFFICE/DocSpace-server/blob/v3.0.4-server/products/ASC.People/Server/ApiModels/ResponseDto/FileUploadResultDto.cs/


class Response(Protocol):
    request: HTTPRequest


class SuccessResponse(Response):
    request: HTTPRequest
    response: HTTPResponse
    payload: SuccessPayload


    def __init__(self, request: HTTPRequest, response: HTTPResponse):
        self.request = request
        self.response = response
        self.payload = SuccessPayload()


    @property
    def content(self) -> Any:
        if self.payload.response is not None:
            return self.payload.response

        if self.payload.data is not None:
            return self.payload.data

        return None


class ErrorResponse(Response):
    request: HTTPRequest
    exception: Exception
    payload: ErrorPayload


    def __init__(self, request: HTTPRequest, exception: Exception):
        self.request = request
        self.exception = exception
        self.payload = ErrorPayload()


    @property
    def content(self) -> Any:
        return self.payload.error


class SuccessPayload(BaseModel):
    response: Any = Field(None)
    count: int | None = Field(None)
    total: int | None = Field(None)
    links: list[ResponseLink] | None = Field(None)
    status: int | None = Field(None)
    statusCode: int | None = Field(None)
    data: Any = Field(None)
    success: bool | None = Field(None)


class ErrorPayload(BaseModel):
    error: ResponseError | None = Field(None)
    status: int | None = Field(None)
    statusCode: int | None = Field(None)


class ResponseLink(BaseModel):
    href: str | None = Field(None)
    action: str | None = Field(None)


class ResponseError(BaseModel):
    message: str | None = Field(None)
    type: str | None = Field(None)
    stack: str | None = Field(None)
    hresult: int | None = Field(None)
