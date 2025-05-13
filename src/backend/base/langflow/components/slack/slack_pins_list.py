from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.slack import (
    Component,
    DataOutput,
    OAuthTokenInput,
    PinListOptions,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Lists items pinned to a channel."
DESCRIPTION_CHANNEL = "Channel to get pinned items for."


class SlackGetPins(Component):
    display_name = "Get List of Pins"
    description = DESCRIPTION_COMPONENT
    name = "SlackGetPins"

    inputs = [
        OAuthTokenInput(),
        MessageTextInput(
            name="channel",
            display_name="Channel ID",
            info=DESCRIPTION_CHANNEL
        )
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        channel: str = Field(..., description=DESCRIPTION_CHANNEL)


    def _create_schema(self) -> Schema:
        return self.Schema(
            channel=self.channel
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._get_pins(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="slack_get_pins",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return self._get_pins(schema)


    def _get_pins(self, schema: Schema) -> Any:
        client = self._get_client()

        options = PinListOptions(channel=schema.channel)

        result, response = client.pin.get_list(options)

        return result
