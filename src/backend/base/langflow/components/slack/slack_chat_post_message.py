from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.slack import OAuthTokenInput, Component, DataOutput, PostMessageOptions, ToolOutput
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Sends a message to a channel."
DESCRIPTION_CHANNEL = "Channel ID or name that represents a channel, group, or IM channel to send the message to."
DESCRIPTION_TEXT = "Message text to post."


class SlackPostMessage(Component):
    display_name = "Post Message"
    description = DESCRIPTION_COMPONENT
    name = "SlackPostMessage"


    inputs = [
        OAuthTokenInput(),
        MessageTextInput(
            name="channel",
            display_name="Channel",
            info=DESCRIPTION_CHANNEL
        ),
        MessageTextInput(
            name="text",
            display_name="Text",
            info=DESCRIPTION_TEXT
        )
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        channel: str = Field(..., description=DESCRIPTION_CHANNEL)
        text: str = Field(..., description=DESCRIPTION_TEXT)


    def _create_schema(self) -> Schema:
        return self.Schema(
            channel=self.channel,
            text=self.text
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._post_message(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="slack_post_message",
            description=DESCRIPTION_COMPONENT,
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return self._post_message(schema)


    def _post_message(self, schema: Schema) -> Any:
        client = self._get_client()

        options = PostMessageOptions(channel=schema.channel, text=schema.text)

        result, response = client.chat.post_message(options)

        return result
