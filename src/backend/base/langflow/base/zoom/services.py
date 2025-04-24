import base64

from pydantic import BaseModel, Field

from .base import Service


class AuthBody(BaseModel):
    account_id: str | None = Field(None, alias="account_id")
    grant_type: str | None = Field(None, alias="grant_type")


class AuthOptions(BaseModel):
    api_url: str | None = Field(None, alias="api_url")
    account_id: str | None = Field(None, alias="account_id")
    client_id: str | None = Field(None, alias="client_id")
    client_secret: str | None = Field(None, alias="client_secret")


class AuthService(Service):
    def auth(self, options: AuthOptions):
        if options.api_url:
            self._client.api_url = options.api_url

        credentials = f"{options.client_id}:{options.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        body = AuthBody(
            account_id=options.account_id,
            grant_type="account_credentials"
        )


        return self._client.request(
            "POST",
            "/oauth/token",
            headers=headers,
            body=body.model_dump(exclude_none=True, by_alias=True),
        )
