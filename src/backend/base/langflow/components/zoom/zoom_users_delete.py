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

DESCRIPTION_COMPONENT = "Disassociate (unlink) a user or permanently delete a user."
DESCRIPTION_USER_ID = "The user's user ID or email address. For user-level apps, pass the 'me' value."
DESCRIPTION_ACTION = "Delete action options.\n'disassociate' - Disassociate a user.\n'delete' - Permanently delete a user."  # noqa: E501
DESCRIPTION_ENCRYPTED_EMAIL = "Whether the email address passed for the 'userId' value is an encrypted email address."
DESCRIPTION_TRANSFER_EMAIL = "This boolean field is required if the user has Zoom Events/Sessions feature. After you delete or disassociate the user, the user's hub assets on Zoom Events site will be transferred to the target user."  # noqa: E501

class ZoomUsersDelete(Component):
    display_name = "Delete User"
    description = DESCRIPTION_COMPONENT
    name = "ZoomUsersDelete"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="zoom_user_id",
            display_name="User ID",
            info=DESCRIPTION_USER_ID,
            required=True
        ),
        MessageTextInput(
            name="action",
            display_name="Action",
            info=DESCRIPTION_ACTION
        ),
        MessageTextInput(
            name="transfer_email",
            display_name="Transfer Email",
            info=DESCRIPTION_TRANSFER_EMAIL,
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
        action: str | None = Field(None, description=DESCRIPTION_ACTION)
        transfer_email: str | None = Field(None, description=DESCRIPTION_TRANSFER_EMAIL)
        encrypted_email: str | None = Field(None, description=DESCRIPTION_ENCRYPTED_EMAIL)


    def _create_schema(self) -> Schema:
        return self.Schema(
            user_id=self.zoom_user_id,
            action=self.action,
            transfer_email=self.transfer_email,
            encrypted_email=self.encrypted_email
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._delete(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="zoom_users_delete",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._delete(schema)


    def _delete(self, schema: Schema) -> list[Any]:
        client = self._get_client()

        result, response = client.users.delete(
            schema.user_id,
            schema.action,
            schema.transfer_email,
            schema.encrypted_email
        )

        return result
