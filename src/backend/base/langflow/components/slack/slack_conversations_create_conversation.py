
from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.slack import (
    INPUT_DESCRIPTION_IS_PRIVATE,
    AuthTextInput,
    Component,
    CreateConversationOptions,
    DataOutput,
    IsPrivateInput,
    IsPrivateMixin,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data


class SlackCreateConversation(Component, IsPrivateMixin):
    display_name = "Create Conversation"
    description = "Initiates a public or private channel-based conversation"
    name = "SlackCreateConversation"

    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="conversation_name",
            display_name="Name",
            info="The name of the conversation."
        ),
        MessageTextInput(
            name="team_id",
            display_name="Team ID",
            info="The ID of the team to create the conversation in.",
            advanced=True
        ),
        IsPrivateInput()
    ]

    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        name: str = Field(..., description="The name of the conversation.")
        team_id: str | None = Field(None, description="The ID of the team to create the conversation in.")
        is_private: bool | None = Field(None, description=INPUT_DESCRIPTION_IS_PRIVATE)


    def _create_schema(self) -> Schema:
        return self.Schema(
            name=self.conversation_name,
            team_id=self.team_id,
            is_private=self.is_private
        )


    async def build_data(self) -> Data:
        schema = self._create_schema()
        data = await self._create_conversation(schema)
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
        return self._create_conversation(schema)


    async def _create_conversation(self, schema: Schema) -> Any:
        client = await self._get_client()

        options = CreateConversationOptions(name=schema.name, team_id=schema.team_id, is_private=schema.is_private)

        result, response = client.conversation.create_conversation(options)

        return result
