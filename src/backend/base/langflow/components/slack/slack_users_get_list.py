from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel

from langflow.base.slack import OAuthTokenInput, Component, DataOutput, ToolOutput
from langflow.field_typing import Tool
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Lists all users in a Slack team."


class SlackGetUsers(Component):
    display_name = "Get Users"
    description = DESCRIPTION_COMPONENT
    name = "SlackGetUsers"


    inputs = [
        OAuthTokenInput()
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        pass


    def build_data(self) -> Data:
        data = self._get_users()
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="slack_get_users",
            description=DESCRIPTION_COMPONENT,
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self) -> Any:
        return self._get_users()


    def _get_users(self) -> Any:
        client = self._get_client()

        result, response = client.user.get_list()

        return result
