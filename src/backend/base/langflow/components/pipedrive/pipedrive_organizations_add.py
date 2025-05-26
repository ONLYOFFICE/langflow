from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.pipedrive import (
    AddOrganizationOptions,
    AuthTextInput,
    Component,
    DataOutput,
    OwnerIdInput,
    OwnerIdMixin,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Adds a new organization"
DESCRIPTION_NAME = "The name of the organization"
DESCRIPTION_OWNER_ID = "The ID of the user who owns the organization"


class PipedriveOrganizationsAdd(Component, OwnerIdMixin):
    display_name = "Add an Organization"
    description = DESCRIPTION_COMPONENT
    name = "PipedriveOrganizationsAdd"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="organization_name",
            display_name="Name",
            info=DESCRIPTION_NAME,
        ),
        OwnerIdInput(info=DESCRIPTION_OWNER_ID)
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        name: str | None = Field(None, description=DESCRIPTION_NAME)
        owner_id: int | None = Field(None, description=DESCRIPTION_OWNER_ID)


    def _create_schema(self) -> Schema:
        return self.Schema(
            name=self.organization_name,
            owner_id=self.owner_id,
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._add(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="pipedrive_organizations_add",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._add(schema)


    def _add(self, schema: Schema) -> Any:
        client = self._get_client()

        options = AddOrganizationOptions(
            name=schema.name,
            owner_id=schema.owner_id,
        )

        result, response = client.organizations.add(options)

        return result

