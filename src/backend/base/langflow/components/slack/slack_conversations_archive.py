from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.slack import (
    ArchiveConversationOptions,
    AuthTextInput,
    Component,
    DataOutput,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Archives a conversation."
DESCRIPTION_CHANNEL = "ID of conversation to archive."


class SlackArchiveConversation(Component):
    display_name = "Archive Conversation"
    description = DESCRIPTION_COMPONENT
    name = "SlackArchiveConversation"


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
        data = await self._archive_conversation(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="slack_archive_conversation",
            description=DESCRIPTION_COMPONENT,
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return self._archive_conversation(schema)


    async def _archive_conversation(self, schema: Schema) -> Any:
        client = await self._get_client()

        options = ArchiveConversationOptions(channel=schema.channel)

        result, response = client.conversation.archive(options)

        return result
