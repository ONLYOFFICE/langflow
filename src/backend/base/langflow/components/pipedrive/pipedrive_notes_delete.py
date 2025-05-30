from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.pipedrive import (
    AuthTextInput,
    Component,
    DataOutput,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Deletes a specific note"
DESCRIPTION_NOTE_ID = "The ID of the note to delete"


class PipedriveNotesDelete(Component):
    display_name = "Delete a Note"
    description = DESCRIPTION_COMPONENT
    name = "PipedriveNotesDelete"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="note_id",
            display_name="Note ID",
            info=DESCRIPTION_NOTE_ID,
            required=True,
        ),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        note_id: str = Field(..., description=DESCRIPTION_NOTE_ID)


    def _create_schema(self) -> Schema:
        return self.Schema(
            note_id=self.note_id,
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._delete(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="pipedrive_notes_delete",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._delete(schema)


    def _delete(self, schema: Schema) -> Any:
        client = self._get_client()

        result, response = client.notes.delete(schema.note_id)

        return result
