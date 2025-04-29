from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel

from langflow.base.slack import (
    OAuthTokenInput,
    Component,
    DataOutput,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Lists all channels in a Slack team."


class SlackGetConversations(Component):
    display_name = "Get Conversations"
    description = DESCRIPTION_COMPONENT
    name = "SlackGetConversations"


    inputs = [
        OAuthTokenInput(),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        pass


    def build_data(self) -> Data:
        data = self._get_conversations()
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="slack_get_conversations",
            description=DESCRIPTION_COMPONENT,
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self) -> Any:
        return self._get_conversations()


    def _get_conversations(self) -> Any:
        client = self._get_client()

        result, response = client.conversation.get_list()

        return result
