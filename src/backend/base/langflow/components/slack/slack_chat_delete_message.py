from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.slack import Component, DataOutput, DeleteMessageOptions, OAuthTokenInput, ToolOutput
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Deletes a message."
DESCRIPTION_CHANNEL = "Channel containing the message to be deleted."
DESCRIPTION_TIMESTAMP = "Timestamp of the message to be deleted."


class SlackDeleteMessage(Component):
    display_name = "Delete Message"
    description = DESCRIPTION_COMPONENT
    name = "SlackDeleteMessage"


    inputs = [
        OAuthTokenInput(),
        MessageTextInput(
            name="channel",
            display_name="Channel ID",
            info=DESCRIPTION_CHANNEL
        ),
        MessageTextInput(
            name="timestamp",
            display_name="Timestamp",
            info=DESCRIPTION_TIMESTAMP
        )
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        channel: str = Field(..., description=DESCRIPTION_CHANNEL)
        timestamp: str = Field(..., description=DESCRIPTION_TIMESTAMP)


    def _create_schema(self) -> Schema:
        return self.Schema(
            channel=self.channel,
            timestamp=self.timestamp
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._delete_message(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="slack_delete_message",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return self._delete_message(schema)


    def _delete_message(self, schema: Schema) -> Any:
        client = self._get_client()

        options = DeleteMessageOptions(channel=schema.channel, ts=schema.timestamp)

        result, response = client.chat.delete_message(options)

        return result
