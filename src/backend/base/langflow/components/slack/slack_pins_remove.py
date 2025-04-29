from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.slack import (
    OAuthTokenInput,
    Component,
    DataOutput,
    PinOptions,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Un-pins an item from a channel."
DESCRIPTION_CHANNEL = "Channel where the item is pinned to."
DESCRIPTION_TIMESTAMP = "Timestamp of the message to un-pin."


class SlackUnpinMessage(Component):
    display_name = "Un-pin Message"
    description = DESCRIPTION_COMPONENT
    name = "SlackUnpinMessage"

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
        ),
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
        data = self._unpin(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="slack_unpin",
            description=DESCRIPTION_COMPONENT,
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return self._unpin(schema)


    def _unpin(self, schema: Schema) -> Any:
        client = self._get_client()

        options = PinOptions(channel=schema.channel, timestamp=schema.timestamp)

        result, response = client.pin.unpin(options)

        return result
