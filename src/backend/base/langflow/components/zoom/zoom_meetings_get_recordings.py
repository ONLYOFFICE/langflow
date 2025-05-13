from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.zoom import (
    DESCRIPTION_MEETING_ID,
    AuthTextInput,
    Component,
    DataOutput,
    GetRecordingsOptions,
    MeetingIdInput,
    MeetingIdMixin,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Lists all cloud recordings for a user. For user-level apps, pass the 'me' value instead of the 'userId' parameter."  # noqa: E501
DESCRIPTION_USER_ID = "The user's ID or email address. For user-level apps, pass the 'me' value."
DESCRIPTION_FROM = "The start date in 'yyyy-mm-dd' UTC format for the date range where you would like to retrieve recordings."  # noqa: E501
DESCRIPTION_TO = "The end date in 'yyyy-mm-dd' 'yyyy-mm-dd' UTC format."


class ZoomMeetingsGetRecordings(Component, MeetingIdMixin):
    display_name = "Get Recordings"
    description = DESCRIPTION_COMPONENT
    name = "ZoomMeetingsGetRecordings"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="zoom_user_id",
            display_name="User ID",
            info=DESCRIPTION_USER_ID,
            required=True
        ),
        MeetingIdInput(),
        MessageTextInput(
            name="from_",
            display_name="From",
            info=DESCRIPTION_FROM
        ),
        MessageTextInput(
            name="to",
            display_name="To",
            info=DESCRIPTION_TO
        ),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        user_id: str = Field(..., description=DESCRIPTION_USER_ID)
        meeting_id: str | None = Field(None, description=DESCRIPTION_MEETING_ID)
        from_: str | None = Field(None, description=DESCRIPTION_FROM)
        to: str | None = Field(None, description=DESCRIPTION_TO)


    def _create_schema(self) -> Schema:
        return self.Schema(
            user_id=self.zoom_user_id,
            meeting_id=self.meeting_id,
            from_=self.from_,
            to=self.to
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._get_recordings(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="zoom_meetings_get_recordings",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._get_recordings(schema)


    def _get_recordings(self, schema: Schema) -> list[Any]:
        client = self._get_client()

        options = GetRecordingsOptions(
            meeting_id=schema.meeting_id,
            from_=schema.from_,
            to=schema.to
        )

        result, response = client.meetings.get_recordings(schema.user_id, options)

        return result
