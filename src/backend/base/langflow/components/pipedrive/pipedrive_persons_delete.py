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

DESCRIPTION_COMPONENT = "Marks a person as deleted. After 30 days, the person will be permanently deleted"
DESCRIPTION_PERSON_ID = "The ID of the person to delete"


class PipedrivePersonsDelete(Component):
    display_name = "Delete a Person"
    description = DESCRIPTION_COMPONENT
    name = "PipedrivePersonsDelete"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="person_id",
            display_name="Person ID",
            info=DESCRIPTION_PERSON_ID,
            required=True,
        ),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        person_id: str = Field(..., description=DESCRIPTION_PERSON_ID)


    def _create_schema(self) -> Schema:
        return self.Schema(
            person_id=self.person_id,
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._delete(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="pipedrive_persons_delete",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._delete(schema)


    def _delete(self, schema: Schema) -> Any:
        client = self._get_client()

        result, response = client.persons.delete(schema.person_id)

        return result
