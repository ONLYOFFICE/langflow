from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.slack import (
    INPUT_DESCRIPTION_FORCE,
    AuthTextInput,
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


class SlackInviteUsers(Component, ForceMixin):
    display_name = "Invite Users"
    description = "Invites users to a channel."
    name = "SlackInviteUsers"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="channel",
            display_name="Channel ID",
            info="The ID of the public or private channel to invite user(s) to."
        ),
        MessageTextInput(
            name="users",
            display_name="Users",
            info="A comma separated list of user IDs."
        ),
        ForceInput()
    ]

    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        channel: str = Field(..., description="The ID of the public or private channel to invite user(s) to.")
        users: str = Field(..., description="A comma separated list of user IDs.")
        force: bool | None = Field(None, description=INPUT_DESCRIPTION_FORCE)


    def _create_schema(self) -> Schema:
        return self.Schema(
            channel=self.channel,
            users=self.users,
            force=self.force
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._invite(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="slack_invite_users",
            description="Invites users to a channel.",
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return self._invite(schema)


    async def _invite(self, schema: Schema) -> Any:
        client = await self._get_client()

        options = InviteOptions(channel=schema.channel, users=schema.users, force=schema.force)

        result, response = client.conversation.invite(options)

        return result
