from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.slack import (
    Component,
    DataOutput,
    KickOptions,
    OAuthTokenInput,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Removes a user from a conversation."
DESCRIPTION_CHANNEL = "ID of conversation to remove user from."
DESCRIPTION_USER = "User ID to be removed."


class SlackKickUser(Component):
    display_name = "Kick User"
    description = DESCRIPTION_COMPONENT
    name = "SlackKickUser"


    inputs = [
        OAuthTokenInput(),
        MessageTextInput(
            name="channel",
            display_name="Channel ID",
            info=DESCRIPTION_CHANNEL
        ),
        MessageTextInput(
            name="user",
            display_name="User",
            info=DESCRIPTION_USER
        )
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        channel: str = Field(..., description=DESCRIPTION_CHANNEL)
        user: str = Field(..., description=DESCRIPTION_USER)


    def _create_schema(self) -> Schema:
        return self.Schema(
            channel=self.channel,
            user=self.user
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._kick(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="slack_kick_user",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return self._kick(schema)


    def _kick(self, schema: Schema) -> Any:
        client = self._get_client()

        options = KickOptions(channel=schema.channel, user=schema.user)

        result, response = client.conversation.kick(options)

        return result
