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

DESCRIPTION_COMPONENT = "List a meeting host user's scheduled meetings. For user-level apps, pass the 'me' value instead of the 'userId' parameter."  # noqa: E501
DESCRIPTION_USER_ID = "The user's user ID or email address. For user-level apps, pass the 'me' value."
DESCRIPTION_TYPE = "The type of meeting.\n'scheduled' - All valid previous (unexpired) meetings, live meetings, and upcoming scheduled meetings.\n'live' - All the ongoing meetings.\n'upcoming' - All upcoming meetings, including live meetings.\n'upcoming_meetings' - All upcoming meetings, including live meetings.\n'previous_meetings' - All the previous meetings."  # noqa: E501
DESCRIPTION_FROM = "The start date."
DESCRIPTION_TO = "The end date."
DESCRIPTION_TIMEZONE = "The timezone to assign to the from and to value."


class ZoomMeetingsGetList(Component):
    display_name = "Get Meetings List"
    description = DESCRIPTION_COMPONENT
    name = "ZoomMeetingsGetList"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="zoom_user_id",
            display_name="User ID",
            info=DESCRIPTION_USER_ID,
            required=True
        ),
        MessageTextInput(
            name="type",
            display_name="Type",
            info=DESCRIPTION_TYPE
        ),
        MessageTextInput(
            name="from_",
            display_name="From",
            info=DESCRIPTION_FROM,
            advanced=True
        ),
        MessageTextInput(
            name="to",
            display_name="To",
            info=DESCRIPTION_TO,
            advanced=True
        ),
        MessageTextInput(
            name="timezone",
            display_name="Timezone",
            info=DESCRIPTION_TIMEZONE,
            advanced=True
        ),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        user_id: str = Field(..., description=DESCRIPTION_USER_ID)
        type: str | None = Field(None, description=DESCRIPTION_TYPE)
        from_: str | None = Field(None, description=DESCRIPTION_FROM)
        to: str | None = Field(None, description=DESCRIPTION_TO)
        timezone: str | None = Field(None, description=DESCRIPTION_TIMEZONE)


    def _create_schema(self) -> Schema:
        return self.Schema(
            user_id=self.zoom_user_id,
            type=self.type,
            from_=self.from_,
            to=self.to,
            timezone=self.timezone
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._get_list(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="zoom_meetings_get_list",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._get_list(schema)


    def _get_list(self, schema: Schema) -> list[Any]:
        client = self._get_client()

        result, response = client.meetings.get_list(
            schema.user_id,
            schema.type,
            schema.from_,
            schema.to,
            schema.timezone
        )

        return result
