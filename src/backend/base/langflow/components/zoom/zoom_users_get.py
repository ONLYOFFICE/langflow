from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.zoom import (
    AuthTextInput,
    Component,
    DataOutput,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "View a user's information on a Zoom account. For user-managed apps, pass the 'me' value instead of the 'userId' parameter."  # noqa: E501
DESCRIPTION_USER_ID = "The user's user ID or email address. For user-level apps, pass the 'me' value."
DESCRIPTION_LOGIN_TYPE = "The user's login method.\n0 - Facebook OAuth\n1 - Google OAuth.\n24 - Apple OAuth.\n27 - Microsoft OAuth.\n97 - Mobile device.\n98 - RingCentral OAuth.\n99 - API user.\n100 - Zoom Work email.\n101 - Single Sign-On (SSO).\nThese login methods are only available in China.\n11 - Phone number.\n21 - WeChat.\n23 - Alipay."  # noqa: E501
DESCRIPTION_ENCRYPTED_EMAIL = "Whether the email address passed for the 'userId' value is an encrypted email address."

class ZoomUsersGetUser(Component):
    display_name = "Get User"
    description = DESCRIPTION_COMPONENT
    name = "ZoomUsersGetUser"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="zoom_user_id",
            display_name="User ID",
            info=DESCRIPTION_USER_ID,
            required=True
        ),
        MessageTextInput(
            name="login_type",
            display_name="Login Type",
            info=DESCRIPTION_LOGIN_TYPE,
            advanced=True
        ),
        MessageTextInput(
            name="encrypted_email",
            display_name="Encrypted Email",
            info=DESCRIPTION_ENCRYPTED_EMAIL,
            advanced=True
        ),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        user_id: str = Field(..., description=DESCRIPTION_USER_ID)
        login_type: str | None = Field(None, description=DESCRIPTION_LOGIN_TYPE)
        encrypted_email: str | None = Field(None, description=DESCRIPTION_ENCRYPTED_EMAIL)


    def _create_schema(self) -> Schema:
        return self.Schema(
            user_id=self.zoom_user_id,
            login_type=self.login_type,
            encrypted_email=self.encrypted_email
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._get(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="zoom_users_get_user",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._get(schema)


    def _get(self, schema: Schema) -> list[Any]:
        client = self._get_client()

        result, response = client.users.get(
            schema.user_id,
            schema.login_type,
            schema.encrypted_email
        )

        return result
