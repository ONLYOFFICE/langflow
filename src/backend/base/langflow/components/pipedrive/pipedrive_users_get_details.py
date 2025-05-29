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

DESCRIPTION_COMPONENT = "Returns data about a specific user within the company"
DESCRIPTION_USER_ID = "The ID of the user"


class PipedriveUsersGetDetails(Component):
    display_name = "Get a User"
    description = DESCRIPTION_COMPONENT
    name = "PipedriveUsersGetDetails"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="pipedrive_user_id",
            display_name="User ID",
            info=DESCRIPTION_USER_ID,
            required=True,
        ),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        user_id: str = Field(..., description=DESCRIPTION_USER_ID)


    def _create_schema(self) -> Schema:
        return self.Schema(
            user_id=self.pipedrive_user_id,
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._get_details(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="pipedrive_users_get_details",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._get_details(schema)


    def _get_details(self, schema: Schema) -> Any:
        client = self._get_client()

        result, response = client.users.get_details(schema.user_id)

        return result
