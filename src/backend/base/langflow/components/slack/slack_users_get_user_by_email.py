from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.slack import OAuthTokenInput, Component, DataOutput, GetUserByEmailOptions, ToolOutput
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Find a user with an email address."
DESCRIPTION_EMAIL = "An email address belonging to a user in the workspace."


class SlackGetUserByEmail(Component):
    display_name = "Get User by Email"
    description = DESCRIPTION_COMPONENT
    name = "SlackGetUserByEmail"


    inputs = [
        OAuthTokenInput(),
        MessageTextInput(
            name="email",
            display_name="Email",
            info=DESCRIPTION_EMAIL
        ),
    ]

    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        email: str = Field(..., description=DESCRIPTION_EMAIL)


    def _create_schema(self) -> Schema:
        return self.Schema(
            email=self.email
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._get_user_by_email(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="slack_get_user_by_email",
            description=DESCRIPTION_COMPONENT,
            coroutine=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> Any:
        schema = self.Schema(**kwargs)
        return self._get_user_by_email(schema)


    def _get_user_by_email(self, schema: Schema) -> Any:
        client = self._get_client()

        options = GetUserByEmailOptions(email=schema.email)

        result, response = client.user.get_user_by_email(options)

        return result
