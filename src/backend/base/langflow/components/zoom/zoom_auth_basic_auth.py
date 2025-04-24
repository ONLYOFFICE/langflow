import json

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.zoom import AuthOptions, Client, DataOutput, ToolOutput
from langflow.custom.custom_component.component_with_cache import ComponentWithCache
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput, SecretStrInput
from langflow.schema import Data
from langflow.schema.message import Message
from langflow.template import Output

DESCRIPTION_COMPONENT = "Basic authentication for Zoom."
DESCRIPTION_API_URL = "The base URL of the Zoom instance."
DESCRIPTION_ACCOUNT_ID = "The account ID to access the Zoom API."
DESCRIPTION_CLIENT_ID = "The client ID to access the Zoom API."
DESCRIPTION_CLIENT_SECRET = "The client secret to access the Zoom API."  # noqa: S105


class ZoomBasicAuthentication(ComponentWithCache):
    display_name = "Basic Authentication"
    description = DESCRIPTION_COMPONENT
    icon = "zoom"
    name = "ZoomBasicAuthentication"


    inputs = [
        MessageTextInput(
            name="api_url",
            display_name="Zoom API URL",
            info=DESCRIPTION_API_URL,
            value="https://zoom.us",
            advanced=True
        ),
        MessageTextInput(
            name="account_id",
            display_name="Zoom Account ID",
            info=DESCRIPTION_ACCOUNT_ID,
        ),
        MessageTextInput(
            name="client_id",
            display_name="Zoom Client ID",
            info=DESCRIPTION_CLIENT_ID,
        ),
        SecretStrInput(
            name="client_secret",
            display_name="Zoom Client Secret",
            info=DESCRIPTION_CLIENT_SECRET,
        ),
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
        account_id: str = Field(..., description=DESCRIPTION_ACCOUNT_ID)
        client_id: str = Field(..., description=DESCRIPTION_CLIENT_ID)
        client_secret: str = Field(..., description=DESCRIPTION_CLIENT_SECRET)


    def _create_schema(self) -> Schema:
        return self.Schema(
            api_url=self.api_url,
            account_id=self.account_id,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._do_basic(schema)
        return Data(data=data)


    def build_message(self) -> Message:
        schema = self._create_schema()
        data = self._do_basic(schema)

        if "api_url" in data and "token" in data:
            text = f"Base URL: {data['api_url']}\n"
            text += f"Token: {data['token']}"
            return Message(text=text)

        return self.build_text()


    def build_text(self) -> Message:
        schema = self._create_schema()
        data = self._do_basic(schema)
        text = json.dumps(data, indent=4)
        return Message(text=text)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="zoom_auth_basic_auth",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> dict:
        schema = self.Schema(**kwargs)
        return self._do_basic(schema)


    def _do_basic(self, schema: Schema) -> dict:    # TODO: use cache
        client = Client()

        options = AuthOptions(
            api_url=schema.api_url,
            account_id=schema.account_id,
            client_id=schema.client_id,
            client_secret=schema.client_secret,
        )

        result, response = client.auth.auth(options)

        if "api_url" in result and "access_token" in result:
            return {
                "api_url": result["api_url"],
                "token": result["access_token"],
            }

        return json.loads(response.text)
