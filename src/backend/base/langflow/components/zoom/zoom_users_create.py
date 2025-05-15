from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.zoom import (
    AuthTextInput,
    Component,
    CreateUserOptions,
    DataOutput,
    ToolOutput,
    TypeInput,
    TypeMixin,
    UserInfo,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Add a new user to your Zoom account."
DESCRIPTION_ACTION = "The action to take to create the new user. Possible values: 'create', 'autoCreate', 'custCreate', 'ssoCreate'"  # noqa: E501
DESCRIPTION_TYPE = "User type.\n1 - Basic.\n2 - Licensed.\n4 - Unassigned without Meetings Basic.\n99 - None. this can only be set with ssoCreate."  # noqa: E501
DESCRIPTION_EMAIL = "User email address."
DESCRIPTION_FIRST_NAME = "The user's first name. Cannot contain more than 5 Chinese characters."
DESCRIPTION_LAST_NAME = "The user's last name. Cannot contain more than 5 Chinese characters."
DESCRIPTION_DISPLAY_NAME = "The user's display name. Cannot contain more than 10 Chinese characters."
DESCRIPTION_PASSWORD = "User password. Only used for the 'autoCreate' function."  # noqa: S105


class ZoomUsersCreate(Component, TypeMixin):
    display_name = "Create User"
    description = DESCRIPTION_COMPONENT
    name = "ZoomUsersCreate"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="action",
            display_name="Action",
            info=DESCRIPTION_ACTION,
            required=True
        ),
        TypeInput(
            info=DESCRIPTION_TYPE,
            required=True
        ),
        MessageTextInput(
            name="email",
            display_name="Email",
            info=DESCRIPTION_EMAIL,
            required=True
        ),
        MessageTextInput(
            name="zoom_display_name",
            display_name="Display Name",
            info=DESCRIPTION_DISPLAY_NAME
        ),
        MessageTextInput(
            name="first_name",
            display_name="First Name",
            info=DESCRIPTION_FIRST_NAME,
            advanced=True
        ),
        MessageTextInput(
            name="last_name",
            display_name="Last Name",
            info=DESCRIPTION_LAST_NAME,
            advanced=True
        ),
        MessageTextInput(
            name="password",
            display_name="Password",
            info=DESCRIPTION_PASSWORD,
            advanced=True
        ),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        action: str = Field(..., description=DESCRIPTION_ACTION)
        type: int = Field(..., description=DESCRIPTION_TYPE)
        email: str = Field(..., description=DESCRIPTION_EMAIL)
        first_name: str = Field(..., description=DESCRIPTION_FIRST_NAME)
        last_name: str = Field(..., description=DESCRIPTION_LAST_NAME)
        display_name: str = Field(..., description=DESCRIPTION_DISPLAY_NAME)
        password: str = Field(..., description=DESCRIPTION_PASSWORD)


    def _create_schema(self) -> Schema:
        return self.Schema(
            action=self.action,
            type=self.type,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            display_name=self.zoom_display_name,
            password=self.password
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._create(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="zoom_users_create",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._create(schema)


    def _create(self, schema: Schema) -> Any:
        client = self._get_client()

        user_info = UserInfo(
            type=schema.type,
            email=schema.email,
            first_name=schema.first_name,
            last_name=schema.last_name,
            display_name=schema.display_name,
            password=schema.password
        )

        options = CreateUserOptions(
            action=self.action,
            user_info=dict(user_info)
        )

        result, response = client.users.create(options)

        return result
