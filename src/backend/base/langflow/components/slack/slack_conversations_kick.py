from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.slack import (
    AuthTextInput,
    Component,
    DataOutput,
    KickOptions,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data


class SlackKickUser(Component):
    display_name = "Kick User"
    description = "Removes a user from a conversation."
    name = "SlackKickUser"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="channel",
            display_name="Channel ID",
            info="ID of conversation to remove user from."
        ),
        MessageTextInput(
            name="user",
            display_name="User",
            info="User ID to be removed."
        )
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        channel: str = Field(..., description="ID of conversation to remove user from.")
        user: str = Field(..., description="User ID to be removed.")


    def _create_schema(self) -> Schema:
        return self.Schema(
            channel=self.channel,
            user=self.user
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._kick(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="slack_kick_user",
            description="Kicks a user from a conversation.",
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return self._kick(schema)


    async def _kick(self, schema: Schema) -> Any:
        client = await self._get_client()

        options = KickOptions(channel=schema.channel, user=schema.user)

        result, response = client.conversation.kick(options)

        return result
