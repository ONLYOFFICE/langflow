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

DESCRIPTION_COMPONENT = "List users that have registered for a meeting."
DESCRIPTION_MEETING_ID = "The meeting's ID."
DESCRIPTION_STATUS = "Query by the registrant's status.\n'pending' - The registration is pending.\n'approved' - The registrant is approved.\n'denied' - The registration is denied."  # noqa: E501


class ZoomMeetingsGetRegistrants(Component):
    display_name = "Get Registrants List"
    description = DESCRIPTION_COMPONENT
    name = "ZoomMeetingsGetRegistrants"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="meeting_id",
            display_name="Meeting ID",
            info=DESCRIPTION_MEETING_ID,
            required=True
        ),
        MessageTextInput(
            name="meeting_status",
            display_name="Status",
            info=DESCRIPTION_STATUS
        )
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        meeting_id: str = Field(..., description=DESCRIPTION_MEETING_ID)
        meeting_status: str = Field(..., description=DESCRIPTION_STATUS)


    def _create_schema(self) -> Schema:
        return self.Schema(
            meeting_id=self.meeting_id,
            meeting_status=self.meeting_status
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._get_registrants(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="zoom_meetings_get_registrants",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._get_registrants(schema)


    def _get_registrants(self, schema: Schema) -> list[Any]:
        client = self._get_client()

        result, response = client.meetings.get_registrants_list(schema.meeting_id, schema.meeting_status)

        return result
