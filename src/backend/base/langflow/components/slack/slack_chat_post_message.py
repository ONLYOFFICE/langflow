
from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.slack import AuthTextInput, Component, DataOutput, PostMessageOptions, ToolOutput
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data


class SlackPostMessage(Component):
    display_name = "Post Message"
    description = "Post a message to a Slack channel."
    name = "SlackPostMessage"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="channel",
            display_name="Channel",
            info="The channel name to post the message to."
        ),
        MessageTextInput(
            name="text",
            display_name="Text",
            info="The message text to post."
        )
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        channel: str = Field(..., description="The channel name to post the message to.")
        text: str = Field(..., description="The message text to post.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            channel=self.channel,
            text=self.text
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._post_message(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="slack_post_message",
            description="Post a message to a Slack channel.",
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return self._post_message(schema)


    async def _post_message(self, schema: Schema) -> Any:
        client = await self._get_client()

        options = PostMessageOptions(channel=schema.channel, text=schema.text)

        result, response = client.chat.post_message(options)

        return result
