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

DESCRIPTION_COMPONENT = "Retrieve the given meeting's details."
DESCRIPTION_MEETING_ID = "The meeting's ID."


class ZoomMeetingsGet(Component):
    display_name = "Get Meeting"
    description = DESCRIPTION_COMPONENT
    name = "ZoomMeetingsGet"


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
        data = self._get(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="zoom_meetings_get",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._get(schema)


    def _get(self, schema: Schema) -> list[Any]:
        client = self._get_client()

        result, response = client.meetings.get(schema.meeting_id)

        return result
