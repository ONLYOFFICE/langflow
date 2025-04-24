from pydantic import BaseModel, Field

from .base import Service


class ArchiveConversationOptions(BaseModel):
    channel: str | None = Field(None)


class ConversationHistoryOptions(BaseModel):
    channel: str | None = Field(None)
    include_all_metadata: bool | None = Field(None)
    inclusive: bool | None = Field(None)
    latest: str | None = Field(None)
    oldest: str | None = Field(None)
    limit: int | None = Field(None)


class CreateConversationOptions(BaseModel):
    name: str | None = Field(None)
    team_id: str | None = Field(None)
    is_private: bool | None = Field(None)


class DeleteMessageOptions(BaseModel):
    channel: str | None = Field(None)
    ts: str | None = Field(None)


class GetUserByEmailOptions(BaseModel):
    email: str | None = Field(None)


class InviteOptions(BaseModel):
    channel: str | None = Field(None)
    users: str | None = Field(None)
    force: bool | None = Field(None)


class JoinOptions(BaseModel):
    channel: str | None = Field(None)


class KickOptions(BaseModel):
    channel: str | None = Field(None)
    user: str | None = Field(None)


class PinListOptions(BaseModel):
    channel: str | None = Field(None)


class PinOptions(BaseModel):
    channel: str | None = Field(None)
    timestamp: str | None = Field(None)


class PostMessageOptions(BaseModel):
    channel: str | None = Field(None)
    text: str | None = Field(None)


class ChatService(Service):
    def delete_message(self, options: DeleteMessageOptions):
        return self._client.request(
            "POST",
            "https://slack.com/api/chat.delete",
            body=options.model_dump(exclude_none=True, by_alias=True)
        )


    def post_message(self, options: PostMessageOptions):
        return self._client.request(
            "POST",
            "https://slack.com/api/chat.postMessage",
            body=options.model_dump(exclude_none=True, by_alias=True)
        )


class ConversationService(Service):
    def archive(self, options: ArchiveConversationOptions):
        return self._client.request(
            "POST",
            "https://slack.com/api/conversations.archive",
            body=options.model_dump(exclude_none=True, by_alias=True)
        )


    def create_conversation(self, options: CreateConversationOptions):
        return self._client.request(
            "POST",
            "https://slack.com/api/conversations.create",
            body=options.model_dump(exclude_none=True, by_alias=True)
        )


    def get_history(self, options: ConversationHistoryOptions):
        return self._client.request(
            "POST",
            "https://slack.com/api/conversations.history",
            body=options.model_dump(exclude_none=True, by_alias=True)
        )


    def get_list(self):
        return self._client.request(
            "GET",
            "https://slack.com/api/conversations.list"
        )


    def invite(self, options: InviteOptions):
        return self._client.request(
            "POST",
            "https://slack.com/api/conversations.invite",
            body=options.model_dump(exclude_none=True, by_alias=True)
        )


    def join(self, options: JoinOptions):
        return self._client.request(
            "POST",
            "https://slack.com/api/conversations.join",
            body=options.model_dump(exclude_none=True, by_alias=True)
        )


    def kick(self, options: KickOptions):
        return self._client.request(
            "POST",
            "https://slack.com/api/conversations.kick",
            body=options.model_dump(exclude_none=True, by_alias=True)
        )


class PinService(Service):
    def get_list(self, options: PinListOptions):
        return self._client.request(
            "POST",
            "https://slack.com/api/pins.list",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            body=options.model_dump(exclude_none=True, by_alias=True)
        )


    def pin(self, options: PinOptions):
        return self._client.request(
            "POST",
            "https://slack.com/api/pins.add",
            body=options.model_dump(exclude_none=True, by_alias=True)
        )


    def unpin(self, options: PinOptions):
        return self._client.request(
            "POST",
            "https://slack.com/api/pins.remove",
            body=options.model_dump(exclude_none=True, by_alias=True)
        )


class UserService(Service):
    def get_list(self):
        return self._client.request(
            "GET",
            "https://slack.com/api/users.list",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

    def get_user_by_email(self, options: GetUserByEmailOptions):
        return self._client.request(
            "POST",
            "https://slack.com/api/users.lookupByEmail",
            body=options.model_dump(exclude_none=True, by_alias=True),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
