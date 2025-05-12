from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.zoom import (
    DESCRIPTION_DURATION,
    DESCRIPTION_RECURRENCE_END_TIMES,
    DESCRIPTION_RECURRENCE_TYPE,
    DESCRIPTION_SETTINGS,
    DESCRIPTION_TYPE,
    AuthTextInput,
    Component,
    CreateMeetingOptions,
    DataOutput,
    DurationInput,
    DurationMixin,
    RecurrenceEndTimesInput,
    RecurrenceEndTimesMixin,
    RecurrenceOptions,
    RecurrenceTypeInput,
    RecurrenceTypeMixin,
    SettingsInput,
    SettingsMixin,
    ToolOutput,
    TypeInput,
    TypeMixin,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Create a meeting for a user. For user-level apps, pass the 'me' value instead of the 'userId' parameter."  # noqa: E501
DESCRIPTION_USER_ID = "The user's user ID or email address. For user-level apps, pass the 'me' value."
DESCRIPTION_TOPIC = "The meeting's topic."
DESCRIPTION_SCHEDULE_FOR = "The email address or user ID of the user to schedule a meeting for."
DESCRIPTION_START_TIME = "The meeting's start time. This field is only used for scheduled or recurring meetings with a fixed time. This supports local time and GMT formats."  # noqa: E501
DESCRIPTION_TIMEZONE = "The timezone to assign to the start_time value. This field is only used for scheduled or recurring meetings with a fixed time."  # noqa: E501
DESCRIPTION_RECURRENCE_END_DATE_TIME = "Select the final date when the meeting will recur before it is canceled. Should be in UTC time, such as 2017-11-25T12:00:00Z. Cannot be used with 'end_times'."  # noqa: E501
DESCRIPTION_RECURRENCE_WEEKLY_DAYS = "Required if you're scheduling a recurring meeting of type 2 to state the days of the week when the meeting should repeat. For instance, if the meeting should recur on Sundays and Tuesdays, provide '1,3' as this field's value."  # noqa: E501


class ZoomMeetingsCreate(Component,DurationMixin,RecurrenceEndTimesMixin,RecurrenceTypeMixin,SettingsMixin,TypeMixin):
    display_name = "Create Meeting"
    description = DESCRIPTION_COMPONENT
    name = "ZoomMeetingsCreate"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="zoom_user_id",
            display_name="User ID",
            info=DESCRIPTION_USER_ID,
            required=True
        ),
        MessageTextInput(
            name="topic",
            display_name="Topic",
            info=DESCRIPTION_TOPIC
        ),
        TypeInput(),
        MessageTextInput(
            name="schedule_for",
            display_name="Schedule For",
            info=DESCRIPTION_SCHEDULE_FOR,
            advanced=True
        ),
        DurationInput(),
        MessageTextInput(
            name="start_time",
            display_name="Start Time",
            info=DESCRIPTION_START_TIME,
            advanced=True
        ),
        MessageTextInput(
            name="timezone",
            display_name="Timezone",
            info=DESCRIPTION_TIMEZONE,
            advanced=True
        ),
        RecurrenceTypeInput(),
        MessageTextInput(
            name="recurrence_end_date_time",
            display_name="Recurrence End Date Time",
            info=DESCRIPTION_RECURRENCE_END_DATE_TIME,
            advanced=True
        ),
        RecurrenceEndTimesInput(),
        MessageTextInput(
            name="recurrence_weekly_days",
            display_name="Recurrence Weekly Days",
            info=DESCRIPTION_RECURRENCE_WEEKLY_DAYS,
            advanced=True
        ),
        SettingsInput(),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        user_id: str = Field(..., description=DESCRIPTION_USER_ID)
        topic: str | None = Field(None, description=DESCRIPTION_TOPIC)
        type: int | None = Field(None, description=DESCRIPTION_TYPE)
        schedule_for: str | None = Field(None, description=DESCRIPTION_SCHEDULE_FOR)
        duration: int | None = Field(None, description=DESCRIPTION_DURATION)
        start_time: str | None = Field(None, description=DESCRIPTION_START_TIME)
        timezone: str | None = Field(None, description=DESCRIPTION_TIMEZONE)
        recurrence_type: int | None = Field(None, description=DESCRIPTION_RECURRENCE_TYPE)
        recurrence_end_times: int | None = Field(None, description=DESCRIPTION_RECURRENCE_END_TIMES)
        recurrence_end_date_time: str | None = Field(None, description=DESCRIPTION_RECURRENCE_END_DATE_TIME)
        recurrence_weekly_days: str | None = Field(None, description=DESCRIPTION_RECURRENCE_WEEKLY_DAYS)
        settings: dict | None = Field(None, description=DESCRIPTION_SETTINGS)


    def _create_schema(self) -> Schema:
        return self.Schema(
            user_id=self.zoom_user_id,
            topic=self.topic,
            type=self.type,
            schedule_for=self.schedule_for,
            duration=self.duration,
            start_time=self.start_time,
            timezone=self.timezone,
            recurrence_type=self.recurrence_type,
            recurrence_end_times=self.recurrence_end_times,
            recurrence_end_date_time=self.recurrence_end_date_time,
            recurrence_weekly_days=self.recurrence_weekly_days,
            settings=self.settings
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._create_meeting(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="zoom_meetings_create",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._create_meeting(schema)


    def _create_meeting(self, schema: Schema) -> Any:
        client = self._get_client()

        options = CreateMeetingOptions(
            topic=schema.topic,
            type=schema.type,
            schedule_for=schema.schedule_for,
            duration=schema.duration,
            start_time=schema.start_time,
            timezone=schema.timezone,
            settings=schema.settings
        )

        if schema.recurrence_type and options.type == 8:  # noqa: PLR2004
            recurrence = RecurrenceOptions(
                type=schema.recurrence_type,
                end_times=schema.recurrence_end_times,
                end_date_time=schema.recurrence_end_date_time,
                weekly_days=schema.recurrence_weekly_days
            )

            options.recurrence = dict(recurrence)

        result, response = client.meetings.create(schema.user_id, options)

        return result
