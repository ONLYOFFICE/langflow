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

DESCRIPTION_COMPONENT = "Marks an activity as deleted. After 30 days, the activity will be permanently deleted"
DESCRIPTION_ACTIVITY_ID = "The ID of the activity to delete"


class PipedriveActivitiesDelete(Component):
    display_name = "Delete an Activity"
    description = DESCRIPTION_COMPONENT
    name = "PipedriveActivitiesDelete"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="activity_id",
            display_name="Activity ID",
            info=DESCRIPTION_ACTIVITY_ID,
            required=True,
        ),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        activity_id: str = Field(..., description=DESCRIPTION_ACTIVITY_ID)


    def _create_schema(self) -> Schema:
        return self.Schema(
            activity_id=self.activity_id,
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._delete(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="pipedrive_activities_delete",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._delete(schema)


    def _delete(self, schema: Schema) -> Any:
        client = self._get_client()

        result, response = client.activities.delete(schema.activity_id)

        return result
