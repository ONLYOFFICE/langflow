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

DESCRIPTION_COMPONENT = "Returns data about all activities"


class PipedriveActivitiesGetAll(Component):
    display_name = "Get All Activities"
    description = DESCRIPTION_COMPONENT
    name = "PipedriveActivitiesGetAll"


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
        data = self._get_activities()
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="pipedrive_activities_get_all",
            description=DESCRIPTION_COMPONENT,
            func=self._get_activities,
            args_schema=self.Schema,
        )


    def _get_activities(self) -> Any:
        client = self._get_client()

        result, response = client.activities.get_all()

        return result
