from pydantic import BaseModel, Field

from .base import Service


class DeleteMessageOptions(BaseModel):
    channel: str | None = Field(None)
    ts: str | None = Field(None)


class PostMessageOptions(BaseModel):
    channel: str | None = Field(None)
    text: str | None = Field(None)


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


class GetUserByEmailOptions(BaseModel):
    email: str | None = Field(None)


class ChatService(Service):
    def post_message(self, options: PostMessageOptions):
        return self._client.request(
            "POST",
            "https://slack.com/api/chat.postMessage",
            body=options.model_dump(exclude_none=True, by_alias=True)
            )


    def delete_message(self, options: DeleteMessageOptions):
        return self._client.request(
            "POST",
            "https://slack.com/api/chat.delete",
            body=options.model_dump(exclude_none=True, by_alias=True)
        )


class ConversationService(Service):
    def get_list(self):
        return self._client.request(
            "GET",
            "https://slack.com/api/conversations.list"
        )


    def get_history(self, options: ConversationHistoryOptions):
        return self._client.request(
            "POST",
            "https://slack.com/api/conversations.history",
            body=options.model_dump(exclude_none=True, by_alias=True)
        )


    def create_conversation(self, options: CreateConversationOptions):
        return self._client.request(
            "POST",
            "https://slack.com/api/conversations.create",
            body=options.model_dump(exclude_none=True, by_alias=True)
            )


class UserService(Service):
    def get_user_by_email(self, options: GetUserByEmailOptions):
        return self._client.request(
            "POST",
            "https://slack.com/api/users.lookupByEmail",
            body=options.model_dump(exclude_none=True, by_alias=True),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
