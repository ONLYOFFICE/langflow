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

DESCRIPTION_COMPONENT = "Returns data about all not archived deals"


class PipedriveDealsGetAll(Component):
    display_name = "Get All Deals"
    description = DESCRIPTION_COMPONENT
    name = "PipedriveDealsGetAll"


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
        data = self._get_deals()
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="pipedrive_deals_get_all",
            description=DESCRIPTION_COMPONENT,
            func=self._get_deals,
            args_schema=self.Schema,
        )


    def _get_deals(self) -> Any:
        client = self._get_client()

        result, response = client.deals.get_all()

        return result
