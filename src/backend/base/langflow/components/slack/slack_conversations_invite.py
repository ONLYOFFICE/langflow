from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.slack import (
    INPUT_DESCRIPTION_FORCE,
    OAuthTokenInput,
    Component,
    DataOutput,
    ForceInput,
    ForceMixin,
    InviteOptions,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Invites users to a channel."
DESCRIPTION_CHANNEL = "The ID of the public or private channel to invite user(s) to."
DESCRIPTION_USERS = "A comma separated list of user IDs."


class SlackInviteUsers(Component, ForceMixin):
    display_name = "Invite Users"
    description = DESCRIPTION_COMPONENT
    name = "SlackInviteUsers"


    inputs = [
        OAuthTokenInput(),
        MessageTextInput(
            name="channel",
            display_name="Channel ID",
            info=DESCRIPTION_CHANNEL
        ),
        MessageTextInput(
            name="users",
            display_name="Users",
            info=DESCRIPTION_USERS
        ),
        ForceInput()
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        channel: str = Field(..., description=DESCRIPTION_CHANNEL)
        users: str = Field(..., description=DESCRIPTION_USERS)
        force: bool | None = Field(None, description=INPUT_DESCRIPTION_FORCE)


    def _create_schema(self) -> Schema:
        return self.Schema(
            channel=self.channel,
            users=self.users,
            force=self.force
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._invite(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="slack_invite_users",
            description=DESCRIPTION_COMPONENT,
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return self._invite(schema)


    def _invite(self, schema: Schema) -> Any:
        client = self._get_client()

        options = InviteOptions(channel=schema.channel, users=schema.users, force=schema.force)

        result, response = client.conversation.invite(options)

        return result
