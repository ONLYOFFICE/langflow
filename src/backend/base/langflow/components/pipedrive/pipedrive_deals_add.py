from typing import Any

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from langflow.base.pipedrive import (
    AddDealOptions,
    AuthTextInput,
    Component,
    DataOutput,
    OrgIdInput,
    OrgIdMixin,
    OwnerIdInput,
    OwnerIdMixin,
    PersonIdInput,
    PersonIdMixin,
    PipelineIdInput,
    PipelineIdMixin,
    StageIdInput,
    StageIdMixin,
    ToolOutput,
    ValueInput,
    ValueMixin,
)
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

DESCRIPTION_COMPONENT = "Adds a new deal"
DESCRIPTION_TITLE = "The title of the deal"
DESCRIPTION_ORG_ID = "The ID of the organization linked to the deal"
DESCRIPTION_OWNER_ID = "The ID of the user who owns the deal"
DESCRIPTION_PERSON_ID = "The ID of the person linked to the deal"
DESCRIPTION_PIPELINE_ID = "The ID of the pipeline associated with the deal"
DESCRIPTION_CURRENCY = "The currency associated with the deal"
DESCRIPTION_STAGE_ID = "The ID of the deal stage"
DESCRIPTION_VALUE = "The value of the deal"


class PipedriveDealsAdd(Component,OrgIdMixin,OwnerIdMixin,PersonIdMixin,PipelineIdMixin,StageIdMixin,ValueMixin):
    display_name = "Add a Deal"
    description = DESCRIPTION_COMPONENT
    name = "PipedriveDealsAdd"


    inputs = [
        AuthTextInput(),
        MessageTextInput(
            name="title",
            display_name="Title",
            info=DESCRIPTION_TITLE,
            required=True,
        ),
        ValueInput(info=DESCRIPTION_VALUE),
        OwnerIdInput(info=DESCRIPTION_OWNER_ID, advanced=True),
        PersonIdInput(info=DESCRIPTION_PERSON_ID, advanced=True),
        OrgIdInput(info=DESCRIPTION_ORG_ID, advanced=True),
        MessageTextInput(
            name="currency",
            display_name="Currency",
            info=DESCRIPTION_CURRENCY,
            advanced=True,
        ),
        PipelineIdInput(info=DESCRIPTION_PIPELINE_ID, advanced=True),
        StageIdInput(info=DESCRIPTION_STAGE_ID, advanced=True),
    ]


    outputs = [
        DataOutput(),
        ToolOutput(),
    ]


    class Schema(BaseModel):
        title: str = Field(..., description=DESCRIPTION_TITLE)
        value: float | None = Field(None, description=DESCRIPTION_VALUE)
        owner_id: int | None = Field(None, description=DESCRIPTION_OWNER_ID)
        person_id: int | None = Field(None, description=DESCRIPTION_PERSON_ID)
        org_id: int | None = Field(None, description=DESCRIPTION_ORG_ID)
        currency: str | None = Field(None, description=DESCRIPTION_CURRENCY)
        pipeline_id: int | None = Field(None, description=DESCRIPTION_PIPELINE_ID)
        stage_id: int | None = Field(None, description=DESCRIPTION_STAGE_ID)


    def _create_schema(self) -> Schema:
        return self.Schema(
            title=self.title,
            value=self.deal_value,
            owner_id=self.owner_id,
            person_id=self.person_id,
            org_id=self.org_id,
            currency=self.currency,
            pipeline_id=self.pipeline_id,
            stage_id=self.stage_id,
        )


    def build_data(self) -> Data:
        schema = self._create_schema()
        data = self._add(schema)
        return Data(data=data)


    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="pipedrive_deals_add",
            description=DESCRIPTION_COMPONENT,
            func=self._tool_func,
            args_schema=self.Schema,
        )


    def _tool_func(self, **kwargs) -> list[Any]:
        schema = self.Schema(**kwargs)
        return self._add(schema)


    def _add(self, schema: Schema) -> Any:
        client = self._get_client()

        options = AddDealOptions(
            title=schema.title,
            value=schema.value,
            owner_id=schema.owner_id,
            person_id=schema.person_id,
            org_id=schema.org_id,
            currency=schema.currency,
            pipeline_id=schema.pipeline_id,
            stage_id=schema.stage_id,
        )

        result, response = client.deals.add(options)

        return result
