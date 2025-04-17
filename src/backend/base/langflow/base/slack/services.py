from pydantic import BaseModel, Field

from .base import Service


class PostMessageOptions(BaseModel):
    channel: str | None = Field(None)
    text: str | None = Field(None)


class CreateConversationOptions(BaseModel):
    name: str | None = Field(None)
    team_id: str | None = Field(None)
    is_private: bool | None = Field(None)


class ChatService(Service):
    def post_message(self, options: PostMessageOptions):
        return self._client.request(
            "POST",
            "https://slack.com/api/chat.postMessage",
            body=options.model_dump(exclude_none=True, by_alias=True)
            )


class ConversationService(Service):
    def create_conversation(self, options: CreateConversationOptions):
        return self._client.request(
            "POST",
            "https://slack.com/api/conversations.create",
            body=options.model_dump(exclude_none=True, by_alias=True)
            )
