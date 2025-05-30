from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.pipedrive import (
    AddNoteOptions,
    AuthTextInput,
    Component,
    DataOutput,
    DealIdInput,
    DealIdMixin,
    OrgIdInput,
    OrgIdMixin,
    PersonIdInput,
    PersonIdMixin,
    PinnedInput,
    PinnedMixin,
    ProjectIdInput,
    ProjectIdMixin,
    ToolOutput,
    UserIdInput,
    UserIdMixin,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Adds a new note"
DESCRIPTION_CONTENT = "The content of the note in HTML format. Subject to sanitization on the back-end."
DESCRIPTION_USER_ID = "The ID of the user who will be marked as the author of the note. Only an admin can change the author." # noqa: E501
DESCRIPTION_LEAD_ID = "The ID of the lead the note will be attached to. This property is required unless one of ('deal_id', 'person_id', 'org_id', 'project_id') is specified. Format: uuid" # noqa: E501
DESCRIPTION_DEAL_ID = "The ID of the deal the note will be attached to. This property is required unless one of ('lead_id', 'person_id', 'org_id', 'project_id') is specified" # noqa: E501
DESCRIPTION_PERSON_ID = "The ID of the person this note will be attached to. This property is required unless one of ('deal_id', 'lead_id', 'org_id', 'project_id') is specified" # noqa: E501
DESCRIPTION_ORG_ID = "The ID of the organization this note will be attached to. This property is required unless one of ('deal_id', 'lead_id', 'person_id', 'project_id') is specified" # noqa: E501
DESCRIPTION_PROJECT_ID = "The ID of the project the note will be attached to. This property is required unless one of ('deal_id', 'lead_id', 'person_id', 'org_id') is specified" # noqa: E501
DESCRIPTION_PINNED = "Whether the note is pinned to the lead, deal, person, organization, or project"


class PipedriveNotesAdd(Component, DealIdMixin, OrgIdMixin, PersonIdMixin, PinnedMixin, ProjectIdMixin, UserIdMixin):
    display_name = "Add a Note"
    description = DESCRIPTION_COMPONENT
    name = "PipedriveNotesAdd"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="content",
            display_name="Content",
            info=DESCRIPTION_CONTENT,
            required=True,
        ),
        UserIdInput(info=DESCRIPTION_USER_ID),
        MessageTextInput(
            name="lead_id",
            display_name="Lead ID",
            info=DESCRIPTION_LEAD_ID,
            advanced=True,
        ),
        DealIdInput(info=DESCRIPTION_DEAL_ID, advanced=True),
        PersonIdInput(info=DESCRIPTION_PERSON_ID, advanced=True),
        OrgIdInput(info=DESCRIPTION_ORG_ID, advanced=True),
        ProjectIdInput(info=DESCRIPTION_PROJECT_ID, advanced=True),
        PinnedInput(info=DESCRIPTION_PINNED, advanced=True),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        content: str = Field(..., description=DESCRIPTION_CONTENT)
        user_id: int | None = Field(None, description=DESCRIPTION_USER_ID)
        lead_id: str | None = Field(None, description=DESCRIPTION_LEAD_ID)
        deal_id: int | None = Field(None, description=DESCRIPTION_DEAL_ID)
        person_id: int | None = Field(None, description=DESCRIPTION_PERSON_ID)
        org_id: int | None = Field(None, description=DESCRIPTION_ORG_ID)
        project_id: int | None = Field(None, description=DESCRIPTION_PROJECT_ID)
        pinned: bool | None = Field(None, description=DESCRIPTION_PINNED)


    def _create_schema(self) -> Schema:
        return self.Schema(
            content=self.content,
            user_id=self.pipedrive_user_id,
            lead_id=self.lead_id,
            deal_id=self.deal_id,
            person_id=self.person_id,
            org_id=self.org_id,
            project_id=self.project_id,
            pinned=self.pinned,
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

        options = AddNoteOptions(
            content=schema.content,
            user_id=schema.user_id,
            lead_id=schema.lead_id,
            deal_id=schema.deal_id,
            person_id=schema.person_id,
            org_id=schema.org_id,
            project_id=schema.project_id,
            pinned_to_lead_flag=1 if schema.pinned and schema.lead_id else None,
            pinned_to_deal_flag=1 if schema.pinned and schema.deal_id else None,
            pinned_to_person_flag=1 if schema.pinned and schema.person_id else None,
            pinned_to_org_flag=1 if schema.pinned and schema.org_id else None,
            pinned_to_project_flag=1 if schema.pinned and schema.project_id else None,
        )

        result, response = client.notes.add(options)

        return result
