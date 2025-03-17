from __future__ import annotations
from typing import Tuple
from pydantic import BaseModel, Field
from ..base import Response, SuccessResponse, Service


class AuthOptions(BaseModel):
    username: str | None = Field(None, alias="UserName")
    password: str | None = Field(None, alias="Password")


class AuthResponse(BaseModel):
    token: str | None = Field(None)


class AuthService(Service):
    def auth(self, options: AuthOptions) -> Tuple[AuthResponse, Response]:
        payload, response = self._client.post(
            "api/2.0/authentication",
            body=options.model_dump(),
        )

        model: AuthResponse
        if isinstance(response, SuccessResponse):
            model = AuthResponse.model_validate(payload)
        else:
            model = AuthResponse()

        return model, response


    def check(self) -> Tuple[bool, Response]:
        _, response = self._client.get(
            "api/2.0/authentication",
        )

        model: bool
        if isinstance(response, SuccessResponse):
            model = True
        else:
            model = False

        return model, response
