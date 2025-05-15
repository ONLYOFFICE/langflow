import base64

from pydantic import BaseModel, Field

from .base import Service


class AuthBody(BaseModel):
    account_id: str | None = Field(None, alias="account_id")
    grant_type: str | None = Field(None, alias="grant_type")


class AddRegistrantOptions(BaseModel):
    first_name: str | None = Field(None, alias="first_name")
    last_name: str | None = Field(None, alias="last_name")
    email: str | None = Field(None, alias="email")
    auto_approve: bool | None = Field(None, alias="auto_approve")


class AuthOptions(BaseModel):
    api_url: str | None = Field(None, alias="api_url")
    account_id: str | None = Field(None, alias="account_id")
    client_id: str | None = Field(None, alias="client_id")
    client_secret: str | None = Field(None, alias="client_secret")


class CreateMeetingOptions(BaseModel):
    topic: str | None = Field(None, alias="topic")
    type: int | None = Field(None, alias="type")
    schedule_for: str | None = Field(None, alias="schedule_for")
    duration: int | None = Field(None, alias="duration")
    start_time: str | None = Field(None, alias="start_time")
    timezone: str | None = Field(None, alias="timezone")
    settings: dict | None = Field(None, alias="settings")
    recurrence: dict | None = Field(None, alias="recurrence")


class GetRecordingsOptions(BaseModel):
    meeting_id: int | None = Field(None, alias="meeting_id")
    from_: str | None = Field(None, alias="from")
    to: str | None = Field(None, alias="to")


class RecurrenceOptions(BaseModel):
    type: int | None = Field(None, alias="type")
    end_times: int | None = Field(None, alias="end_times")
    end_date_time: str | None = Field(None, alias="end_date_time")
    weekly_days: str | None = Field(None, alias="weekly_days")


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


class MeetingService(Service):
    def add_registrant(self, meeting_id: str, options: AddRegistrantOptions):
        return self._client.request(
            "POST",
            f"/v2/meetings/{meeting_id}/registrants",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


    def create(self, user_id: str, options: CreateMeetingOptions):
        return self._client.request(
            "POST",
            f"/v2/users/{user_id}/meetings",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


    def delete_registrant(self, meeting_id: str, registrant_id: str):
        return self._client.request(
            "DELETE",
            f"/v2/meetings/{meeting_id}/registrants/{registrant_id}",
        )


    def get_recordings(self, user_id: str, options: GetRecordingsOptions):
        return self._client.request(
            "GET",
            f"/v2/users/{user_id}/recordings",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


class UsersService(Service):
    def get_list(self):
        return self._client.request("GET", "/v2/users")
