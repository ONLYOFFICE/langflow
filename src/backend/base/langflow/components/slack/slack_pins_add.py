from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.slack import (
    Component,
    DataOutput,
    OAuthTokenInput,
    PinOptions,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Pins an item to a channel."
DESCRIPTION_CHANNEL = "Channel to pin the message to."
DESCRIPTION_TIMESTAMP = "Timestamp of the message to pin."


class SlackPinMessage(Component):
    display_name = "Pin Message"
    description = DESCRIPTION_COMPONENT
    name = "SlackPinMessage"

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
        data = self._pin(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="slack_pin",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return self._pin(schema)


    def _pin(self, schema: Schema) -> Any:
        client = self._get_client()

        options = PinOptions(channel=schema.channel, timestamp=schema.timestamp)

        result, response = client.pin.pin(options)

        return result
