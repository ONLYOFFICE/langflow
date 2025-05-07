from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel

from langflow.base.zoom import (
    AuthTextInput,
    Component,
    DataOutput,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Retrieve a list your account's users."


class ZoomUsersGetList(Component):
    display_name = "Get Users List"
    description = DESCRIPTION_COMPONENT
    name = "ZoomUsersGetList"


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
        data = self._get_list()
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="zoom_users_get_list",
            description=DESCRIPTION_COMPONENT,
            func=self._get_list,
            args_schema=self.Schema,
        )


    def _get_list(self) -> Any:
        client = self._get_client()

        result, response = client.users.get_list()

        return result
