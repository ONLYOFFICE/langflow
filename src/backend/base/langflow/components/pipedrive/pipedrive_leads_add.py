from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.pipedrive import (
    AddLeadOptions,
    AuthTextInput,
    Component,
    DataOutput,
    OrgIdInput,
    OrgIdMixin,
    OwnerIdInput,
    OwnerIdMixin,
    PersonIdInput,
    PersonIdMixin,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Creates a lead. A lead always has to be linked to a person or an organization or both"
DESCRIPTION_TITLE = "The name of the lead"
DESCRIPTION_OWNER_ID = "The ID of the user which will be the owner of the created lead. If not provided, the user making the request will be used" # noqa: E501
DESCRIPTION_PERSON_ID = "The ID of a person which this lead will be linked to. If the person does not exist yet, it needs to be created first. This property is required unless 'organization_id' is specified." # noqa: E501
DESCRIPTION_ORGANIZATION_ID = "The ID of an organization which this lead will be linked to. If the organization does not exist yet, it needs to be created first. This property is required unless 'person_id' is specified." # noqa: E501


class PipedriveLeadsAdd(Component, PersonIdMixin, OrgIdMixin, OwnerIdMixin):
    display_name = "Add a Lead"
    description = DESCRIPTION_COMPONENT
    name = "PipedriveLeadsAdd"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="title",
            display_name="Title",
            info=DESCRIPTION_TITLE,
            required=True,
        ),
        OwnerIdInput(info=DESCRIPTION_OWNER_ID),
        PersonIdInput(info=DESCRIPTION_PERSON_ID),
        OrgIdInput(info=DESCRIPTION_ORGANIZATION_ID),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        title: str = Field(..., description=DESCRIPTION_TITLE)
        owner_id: int | None = Field(None, description=DESCRIPTION_OWNER_ID)
        person_id: int | None = Field(None, description=DESCRIPTION_PERSON_ID)
        org_id: int | None = Field(None, description=DESCRIPTION_ORGANIZATION_ID)


    def _create_schema(self) -> Schema:
        return self.Schema(
            title=self.title,
            owner_id=self.owner_id,
            person_id=self.person_id,
            org_id=self.org_id,
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._add(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="pipedrive_leads_add",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._add(schema)


    def _add(self, schema: Schema) -> Any:
        client = self._get_client()

        options = AddLeadOptions(
            title=schema.title,
            owner_id=schema.owner_id,
            person_id=schema.person_id,
            org_id=schema.org_id,
        )

        result, response = client.leads.add(options)

        return result

