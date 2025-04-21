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

DESCRIPTION_COMPONENT = "Initiates a public or private channel-based conversation."
DESCRIPTION_CONVERSATION_NAME = "Name of the public or private channel to create."
DESCRIPTION_TEAM_ID = "Encoded team id to create the channel in, required if org token is used."


class SlackCreateConversation(Component, IsPrivateMixin):
    display_name = "Create Conversation"
    description = DESCRIPTION_COMPONENT
    name = "SlackCreateConversation"

    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="conversation_name",
            display_name="Name",
            info=DESCRIPTION_CONVERSATION_NAME
        ),
        MessageTextInput(
            name="team_id",
            display_name="Team ID",
            info=DESCRIPTION_TEAM_ID,
            advanced=True
        ),
        IsPrivateInput()
    ]

    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        name: str = Field(..., description=DESCRIPTION_CONVERSATION_NAME)
        team_id: str | None = Field(None, description=DESCRIPTION_TEAM_ID)
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
            name="slack_create_conversation",
            description=DESCRIPTION_COMPONENT,
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
