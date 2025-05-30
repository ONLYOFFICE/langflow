import json

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.pipedrive import DataOutput, ToolOutput
from langflow.custom import Component
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput, SecretStrInput
from langflow.schema import Data
from langflow.schema.message import Message
from langflow.template import Output

DESCRIPTION_COMPONENT = "Authentication data for Pipedrive."
DESCRIPTION_API_URL = "The base URL of the Pipedrive instance with trailing slash."
DESCRIPTION_TOKEN = "The Pipedrive API token."  # noqa: S105


class PipedriveAuthentication(Component):
    display_name = "Authentication"
    description = DESCRIPTION_COMPONENT
    icon = "pipedrive"
    name = "PipedriveAuthentication"


    inputs = [
        MessageTextInput(
            name="api_url",
            display_name="Pipedrive API URL",
            info=DESCRIPTION_API_URL,
            value="https://certain-root.pipedrive.com/",
            required=True,
        ),
        SecretStrInput(
            name="token",
            display_name="Token",
            info=DESCRIPTION_TOKEN,
            required=True,
        )
    ]


    outputs = [
        DataOutput(),
        Output(
            display_name="Message",
            name="api_build_message",
            method="build_message",
            hidden=True,
        ),
        Output(
            display_name="Text",
            name="api_build_text",
            method="build_text",
            hidden=True,
        ),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        api_url: str = Field(..., description=DESCRIPTION_API_URL)
        token: str = Field(..., description=DESCRIPTION_TOKEN)


    def _create_schema(self) -> Schema:
        return self.Schema(
            api_url=self.api_url,
            token=self.token,
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = dict(schema)
        return Data(data=data)


    def build_message(self) -> Message:
        schema = self._create_schema()
        data = dict(schema)

        if "api_url" in data and "token" in data:
            text = f"Base URL: {data['api_url']}\n"
            text += f"Token: {data['token']}"
            return Message(text=text)

        return self.build_text()


    def build_text(self) -> Message:
        schema = self._create_schema()
        data = dict(schema)
        text = json.dumps(data, indent=4)
        return Message(text=text)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="pipedrive_auth_basic_auth",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> dict:
        schema = self.Schema(**kwargs)
        return dict(schema)
