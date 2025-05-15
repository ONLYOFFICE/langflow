from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.zoom import (
    DESCRIPTION_AUTO_APPROVE,
    AddRegistrantOptions,
    AuthTextInput,
    AutoApproveInput,
    AutoApproveMixin,
    Component,
    DataOutput,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Create and submit a user's registration to a meeting."
DESCRIPTION_MEETING_ID = "The meeting's ID."
DESCRIPTION_FIRST_NAME = "The registrant's first name."
DESCRIPTION_LAST_NAME = "The registrant's last name."
DESCRIPTION_EMAIL = "The registrant's email address."


class ZoomMeetingsAddRegistrant(Component, AutoApproveMixin):
    display_name = "Add Registrant"
    description = DESCRIPTION_COMPONENT
    name = "ZoomMeetingsAddRegistrant"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="meeting_id",
            display_name="Meeting ID",
            info=DESCRIPTION_MEETING_ID,
            required=True
        ),
        MessageTextInput(
            name="email",
            display_name="Email",
            info=DESCRIPTION_EMAIL,
            required=True
        ),
        MessageTextInput(
            name="first_name",
            display_name="First Name",
            info=DESCRIPTION_FIRST_NAME,
            required=True
        ),
        MessageTextInput(
            name="last_name",
            display_name="Last Name",
            info=DESCRIPTION_LAST_NAME
        ),
        AutoApproveInput(),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        meeting_id: str = Field(..., description=DESCRIPTION_MEETING_ID)
        email: str = Field(..., description=DESCRIPTION_EMAIL)
        first_name: str = Field(..., description=DESCRIPTION_FIRST_NAME)
        last_name: str | None = Field(None, description=DESCRIPTION_LAST_NAME)
        auto_approve: bool | None = Field(None, description=DESCRIPTION_AUTO_APPROVE)


    def _create_schema(self) -> Schema:
        return self.Schema(
            meeting_id=self.meeting_id,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            auto_approve=self.auto_approve
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._add_registrant(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="zoom_meetings_add_registrant",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._add_registrant(schema)


    def _add_registrant(self, schema: Schema) -> list[Any]:
        client = self._get_client()

        options = AddRegistrantOptions(
            email=schema.email,
            first_name=schema.first_name,
            last_name=schema.last_name,
            auto_approve=schema.auto_approve
        )

        result, response = client.meetings.add_registrant(schema.meeting_id, options)

        return result
