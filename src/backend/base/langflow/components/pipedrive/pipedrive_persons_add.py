from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.pipedrive import (
    AddPersonOptions,
    AuthTextInput,
    Component,
    DataOutput,
    OrgIdInput,
    OrgIdMixin,
    OwnerIdInput,
    OwnerIdMixin,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Adds a new person"
DESCRIPTION_NAME = "The name of the person"
DESCRIPTION_OWNER_ID = "The ID of the user who owns the person"
DESCRIPTION_ORGANIZATION_ID = "The ID of the organization linked to the person"


class PipedrivePersonsAdd(Component, OrgIdMixin, OwnerIdMixin):
    display_name = "Add a Person"
    description = DESCRIPTION_COMPONENT
    name = "PipedrivePersonsAdd"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="person_name",
            display_name="Name",
            info=DESCRIPTION_NAME,
        ),
        OwnerIdInput(info=DESCRIPTION_OWNER_ID, advanced=True),
        OrgIdInput(info=DESCRIPTION_ORGANIZATION_ID, advanced=True)
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        name: str | None = Field(None, description=DESCRIPTION_NAME)
        owner_id: int | None = Field(None, description=DESCRIPTION_OWNER_ID)
        org_id: int | None = Field(None, description=DESCRIPTION_ORGANIZATION_ID)


    def _create_schema(self) -> Schema:
        return self.Schema(
            name=self.person_name,
            owner_id=self.owner_id,
            org_id=self.org_id,
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._add(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="pipedrive_persons_add",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._add(schema)


    def _add(self, schema: Schema) -> Any:
        client = self._get_client()

        options = AddPersonOptions(
            name=schema.name,
            owner_id=schema.owner_id,
            org_id=schema.org_id,
        )

        result, response = client.persons.add(options)

        return result
