from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.slack import (
    AuthTextInput,
    Component,
    DataOutput,
    JoinOptions,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Joins an existing conversation."
DESCRIPTION_CHANNEL = "ID of conversation to join."


class SlackJoin(Component):
    display_name = "Join Conversation"
    description = DESCRIPTION_COMPONENT
    name = "SlackJoin"

    inputs = [
        AuthTextInput(),
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


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._join(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="slack_join",
            description=DESCRIPTION_COMPONENT,
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return self._join(schema)


    async def _join(self, schema: Schema) -> Any:
        client = await self._get_client()

        options = JoinOptions(channel=schema.channel)

        result, response = client.conversation.join(options)

        return result
