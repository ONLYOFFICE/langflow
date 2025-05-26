from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.pipedrive import (
    AddUserOptions,
    AuthTextInput,
    Component,
    DataOutput,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Add a new user"
DESCRIPTION_EMAIL = "The email of the user"


class PipedriveUsersAdd(Component):
    display_name = "Add a User"
    description = DESCRIPTION_COMPONENT
    name = "PipedriveUsersAdd"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="email",
            display_name="Email",
            info=DESCRIPTION_EMAIL,
            required=True,
        ),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        email: str = Field(..., description=DESCRIPTION_EMAIL)


    def _create_schema(self) -> Schema:
        return self.Schema(
            email=self.email,
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._add(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="pipedrive_users_add",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._add(schema)


    def _add(self, schema: Schema) -> Any:
        client = self._get_client()

        options = AddUserOptions(
            email=schema.email,
        )

        result, response = client.users.add(options)

        return result

