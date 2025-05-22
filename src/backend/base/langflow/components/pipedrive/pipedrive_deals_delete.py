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

DESCRIPTION_COMPONENT = "Marks a deal as deleted. After 30 days, the deal will be permanently deleted"
DESCRIPTION_DEAL_ID = "The ID of the deal to delete"


class PipedriveDealsDelete(Component):
    display_name = "Delete a Deal"
    description = DESCRIPTION_COMPONENT
    name = "PipedriveDealsDelete"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="deal_id",
            display_name="Deal ID",
            info=DESCRIPTION_DEAL_ID,
            required=True,
        ),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        deal_id: str = Field(..., description=DESCRIPTION_DEAL_ID)


    def _create_schema(self) -> Schema:
        return self.Schema(
            deal_id=self.deal_id,
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._delete(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="pipedrive_deals_delete",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._delete(schema)


    def _delete(self, schema: Schema) -> Any:
        client = self._get_client()

        result, response = client.deals.delete(schema.deal_id)

        return result
