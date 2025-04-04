from __future__ import annotations

from pydantic import BaseModel, Field

from langflow.base.onlyoffice.docspace.client.base import Response, Service, SuccessResponse


class AuthOptions(BaseModel):
    username: str | None = Field(None, alias="UserName")
    password: str | None = Field(None, alias="Password")


class AuthResponse(BaseModel):
    token: str | None = Field(None)


class AuthService(Service):
    def auth(self, options: AuthOptions) -> tuple[AuthResponse, Response]:
        payload, response = self._client.post(
            "api/2.0/authentication",
            body=options.model_dump(),
        )

        model = AuthResponse.model_validate(payload) \
            if isinstance(response, SuccessResponse) else AuthResponse()

        return model, response


    def check(self) -> tuple[bool, Response]:
        _, response = self._client.get(
            "api/2.0/authentication",
        )

        model = bool(isinstance(response, SuccessResponse))

        return model, response
