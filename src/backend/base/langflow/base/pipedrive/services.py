from pydantic import BaseModel, Field

from .base import Service


class CreateDealOptions(BaseModel):
    title: str | None = Field(None, alias="title")
    value: float | None = Field(None, alias="value")
    owner_id: int | None = Field(None, alias="owner_id")
    person_id: int | None = Field(None, alias="person_id")
    org_id: int | None = Field(None, alias="org_id")
    currency: str | None = Field(None, alias="currency")
    pipeline_id: int | None = Field(None, alias="pipeline_id")
    stage_id: int | None = Field(None, alias="stage_id")


class DealService(Service):
    def create(self, options: CreateDealOptions) -> dict:
        return self._client.request(
            "POST",
            "api/v2/deals",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )
