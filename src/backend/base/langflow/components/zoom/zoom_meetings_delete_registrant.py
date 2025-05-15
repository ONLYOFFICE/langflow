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

DESCRIPTION_COMPONENT = "Delete a meeting registrant."
DESCRIPTION_MEETING_ID = "The meeting ID."
DESCRIPTION_REGISTRANT_ID = "The meeting registrant ID."


class ZoomMeetingsDeleteRegistrant(Component):
    display_name = "Delete Registrant"
    description = DESCRIPTION_COMPONENT
    name = "ZoomMeetingsDeleteRegistrant"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="meeting_id",
            display_name="Meeting ID",
            info=DESCRIPTION_MEETING_ID,
            required=True
        ),
        MessageTextInput(
            name="registrant_id",
            display_name="Registrant ID",
            info=DESCRIPTION_REGISTRANT_ID,
            required=True
        ),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        meeting_id: str = Field(..., description=DESCRIPTION_MEETING_ID)
        registrant_id: str = Field(..., description=DESCRIPTION_REGISTRANT_ID)


    def _create_schema(self) -> Schema:
        return self.Schema(
            meeting_id=self.meeting_id,
            registrant_id=self.registrant_id
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._delete_registrant(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="zoom_meetings_delete_registrant",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._delete_registrant(schema)


    def _delete_registrant(self, schema: Schema) -> list[Any]:
        client = self._get_client()

        result, response = client.meetings.delete_registrant(schema.meeting_id, schema.registrant_id)

        return result
