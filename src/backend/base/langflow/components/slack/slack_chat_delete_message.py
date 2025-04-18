from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.slack import AuthTextInput, Component, DataOutput, DeleteMessageOptions, ToolOutput
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data


class SlackDeleteMessage(Component):
    display_name = "Delete Message"
    description = "Deletes a message."
    name = "SlackDeleteMessage"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="channel",
            display_name="Channel ID",
            info="Channel containing the message to be deleted."
        ),
        MessageTextInput(
            name="timestamp",
            display_name="Timestamp",
            info="The timestamp of the message to delete."
        )
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        channel: str = Field(..., description="Channel containing the message to be deleted.")
        timestamp: str = Field(..., description="The timestamp of the message to delete.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            channel=self.channel,
            timestamp=self.timestamp
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._delete_message(schema)
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
        return self._delete_message(schema)


    async def _delete_message(self, schema: Schema) -> Any:
        client = await self._get_client()

        options = DeleteMessageOptions(channel=schema.channel, ts=schema.timestamp)

        result, response = client.chat.delete_message(options)

        return result
