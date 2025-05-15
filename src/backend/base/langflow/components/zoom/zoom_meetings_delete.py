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

DESCRIPTION_COMPONENT = "Delete a meeting."
DESCRIPTION_MEETING_ID = "The meeting ID."


class ZoomMeetingsDelete(Component):
    display_name = "Delete Meeting"
    description = DESCRIPTION_COMPONENT
    name = "ZoomMeetingsDelete"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="meeting_id",
            display_name="Meeting ID",
            info=DESCRIPTION_MEETING_ID,
            required=True
        )
    ]

    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        meeting_id: str = Field(..., description=DESCRIPTION_MEETING_ID)


    def _create_schema(self) -> Schema:
        return self.Schema(
            meeting_id=self.meeting_id
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._delete(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="zoom_meetings_delete",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._delete(schema)


    def _delete(self, schema: Schema) -> list[Any]:
        client = self._get_client()

        result, response = client.meetings.delete(schema.meeting_id)

        return result
