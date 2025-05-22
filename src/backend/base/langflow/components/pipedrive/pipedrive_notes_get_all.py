from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel

from langflow.base.pipedrive import (
    AuthTextInput,
    Component,
    DataOutput,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Returns all notes"


class PipedriveNotesGetAll(Component):
    display_name = "Get All Notes"
    description = DESCRIPTION_COMPONENT
    name = "PipedriveNotesGetAll"


    inputs = [
        AuthTextInput(),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        pass


    def build_data(self) -> Data:
        data = self._get_notes()
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="pipedrive_notes_get_all",
            description=DESCRIPTION_COMPONENT,
            func=self._get_notes,
            args_schema=self.Schema,
        )


    def _get_notes(self) -> Any:
        client = self._get_client()

        result, response = client.notes.get_all()

        return result
