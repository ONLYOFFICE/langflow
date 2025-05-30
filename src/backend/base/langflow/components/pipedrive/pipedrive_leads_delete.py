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

DESCRIPTION_COMPONENT = "Deletes a specific lead"
DESCRIPTION_LEAD_ID = "The ID of the lead to delete"


class PipedriveLeadsDelete(Component):
    display_name = "Delete a Lead"
    description = DESCRIPTION_COMPONENT
    name = "PipedriveLeadsDelete"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="lead_id",
            display_name="Lead ID",
            info=DESCRIPTION_LEAD_ID,
            required=True,
        ),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        lead_id: str = Field(..., description=DESCRIPTION_LEAD_ID)


    def _create_schema(self) -> Schema:
        return self.Schema(
            lead_id=self.lead_id,
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._delete(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="pipedrive_leads_delete",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._delete(schema)


    def _delete(self, schema: Schema) -> Any:
        client = self._get_client()

        result, response = client.leads.delete(schema.lead_id)

        return result
