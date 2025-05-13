from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.slack import (
    INPUT_DESCRIPTION_INCLUDE_ALL_METADATA,
    INPUT_DESCRIPTION_INCLUSIVE,
    INPUT_DESCRIPTION_LIMIT,
    Component,
    ConversationHistoryOptions,
    DataOutput,
    IncludeAllMetadataInput,
    IncludeAllMetadataMixin,
    InclusiveInput,
    InclusiveMixin,
    LimitInput,
    LimitMixin,
    OAuthTokenInput,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Fetches a conversation's history of messages and events."
DESCRIPTION_CHANNEL = "Conversation ID to fetch history for."
DESCRIPTION_LATEST = "Only messages before this Unix timestamp will be included in results."
DESCRIPTION_OLDEST = "Only messages after this Unix timestamp will be included in results."


class SlackGetConversationHistory(Component, IncludeAllMetadataMixin, InclusiveMixin, LimitMixin):
    display_name = "Get Conversation History"
    description = DESCRIPTION_COMPONENT
    name = "SlackGetConversationHistory"


    inputs = [
        OAuthTokenInput(),
        MessageTextInput(
            name="channel",
            display_name="Channel ID",
            info=DESCRIPTION_CHANNEL
        ),
        IncludeAllMetadataInput(),
        LimitInput(),
        MessageTextInput(
            name="latest",
            display_name="Latest",
            info=DESCRIPTION_LATEST,
            advanced=True
        ),
        MessageTextInput(
            name="oldest",
            display_name="Oldest",
            info=DESCRIPTION_OLDEST,
            advanced=True
        ),
        InclusiveInput()
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        channel: str = Field(..., description=DESCRIPTION_CHANNEL)
        include_all_metadata: bool | None = Field(None, description=INPUT_DESCRIPTION_INCLUDE_ALL_METADATA)
        limit: int | None = Field(None, description=INPUT_DESCRIPTION_LIMIT)
        latest: str | None = Field(None, description=DESCRIPTION_LATEST)
        oldest: str | None = Field(None, description=DESCRIPTION_OLDEST)
        inclusive: bool | None = Field(None, description=INPUT_DESCRIPTION_INCLUSIVE)


    def _create_schema(self) -> Schema:
        return self.Schema(
            channel=self.channel,
            include_all_metadata=self.include_all_metadata,
            limit=self.limit,
            latest=self.latest,
            oldest=self.oldest,
            inclusive=self.inclusive
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._get_history(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="slack_get_conversation_history",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return self._get_history(schema)


    def _get_history(self, schema: Schema) -> Any:
        client = self._get_client()

        options = ConversationHistoryOptions(
            channel=schema.channel,
            include_all_metadata=schema.include_all_metadata,
            limit=schema.limit,
            latest=schema.latest,
            oldest=schema.oldest,
            inclusive=schema.inclusive
        )

        result, response = client.conversation.get_history(options)

        return result
