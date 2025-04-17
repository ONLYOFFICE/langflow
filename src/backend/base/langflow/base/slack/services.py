from pydantic import BaseModel, Field

from .base import Service


class PostMessageOptions(BaseModel):
    channel: str | None = Field(None)
    text: str | None = Field(None)


class ChatService(Service):
    def post_message(self, options: PostMessageOptions):
        return self._client.request(
            "POST",
            "https://slack.com/api/chat.postMessage",
            body=options.model_dump(exclude_none=True, by_alias=True)
            )
