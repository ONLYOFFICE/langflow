from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.pipedrive import (
    AddActivityOptions,
    AuthTextInput,
    Component,
    DataOutput,
    DealIdInput,
    DealIdMixin,
    OrgIdInput,
    OrgIdMixin,
    OwnerIdInput,
    OwnerIdMixin,
    PersonIdInput,
    PersonIdMixin,
    ProjectIdInput,
    ProjectIdMixin,
    ToolOutput,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Adds a new activity"
DESCRIPTION_SUBJECT = "The subject of the activity"
DESCRIPTION_TYPE = "The type of the activity"
DESCRIPTION_PUBLIC_DESCRIPTION = "The public description of the activity"
DESCRIPTION_OWNER_ID = "The ID of the user who owns the activity"
DESCRIPTION_DEAL_ID = "The ID of the deal linked to the activity"
DESCRIPTION_LEAD_ID = "The ID of the lead linked to the activity"
DESCRIPTION_ORG_ID = "The ID of the organization linked to the activity"
DESCRIPTION_PERSON_ID = "The ID of the person linked to the activity"
DESCRIPTION_PROJECT_ID = "The ID of the project linked to the activity"


class PipedriveActivitiesAdd(Component, DealIdMixin, OrgIdMixin, OwnerIdMixin, PersonIdMixin, ProjectIdMixin):
    display_name = "Add an Activity"
    description = DESCRIPTION_COMPONENT
    name = "PipedriveActivitiesAdd"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="subject",
            display_name="Subject",
            info=DESCRIPTION_SUBJECT,
        ),
        MessageTextInput(
            name="type",
            display_name="Type",
            info=DESCRIPTION_TYPE,
        ),
        MessageTextInput(
            name="public_description",
            display_name="Public Description",
            info=DESCRIPTION_PUBLIC_DESCRIPTION,
        ),
        OwnerIdInput(info=DESCRIPTION_OWNER_ID, advanced=True),
        DealIdInput(info=DESCRIPTION_DEAL_ID, advanced=True),
        MessageTextInput(
            name="lead_id",
            display_name="Lead ID",
            info=DESCRIPTION_LEAD_ID,
            advanced=True,
        ),
        OrgIdInput(info=DESCRIPTION_ORG_ID, advanced=True),
        PersonIdInput(info=DESCRIPTION_PERSON_ID, advanced=True),
        ProjectIdInput(info=DESCRIPTION_PROJECT_ID, advanced=True),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        subject: str | None = Field(None, description=DESCRIPTION_SUBJECT)
        type: str | None = Field(None, description=DESCRIPTION_TYPE)
        public_description: str | None = Field(None, description=DESCRIPTION_PUBLIC_DESCRIPTION)
        owner_id: int | None = Field(None, description=DESCRIPTION_OWNER_ID)
        deal_id: int | None = Field(None, description=DESCRIPTION_DEAL_ID)
        lead_id: str | None = Field(None, description=DESCRIPTION_LEAD_ID)
        org_id: int | None = Field(None, description=DESCRIPTION_ORG_ID)
        person_id: int | None = Field(None, description=DESCRIPTION_PERSON_ID)
        project_id: int | None = Field(None, description=DESCRIPTION_PROJECT_ID)


    def _create_schema(self) -> Schema:
        return self.Schema(
            subject=self.subject,
            type=self.type,
            public_description=self.public_description,
            owner_id=self.owner_id,
            deal_id=self.deal_id,
            lead_id=self.lead_id,
            org_id=self.org_id,
            person_id=self.person_id,
            project_id=self.project_id,
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._add(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="pipedrive_activities_add",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._add(schema)


    def _add(self, schema: Schema) -> Any:
        client = self._get_client()

        options = AddActivityOptions(
            subject=schema.subject,
            type=schema.type,
            public_description=schema.public_description,
            owner_id=schema.owner_id,
            deal_id=schema.deal_id,
            lead_id=schema.lead_id,
            org_id=schema.org_id,
            person_id=schema.person_id,
            project_id=schema.project_id,
        )

        result, response = client.activities.add(options)

        return result

