from pydantic import BaseModel, Field

from .base import Service


class AddActivityOptions(BaseModel):
    subject: str | None = Field(None, alias="subject")
    type: str | None = Field(None, alias="type")
    public_description: str | None = Field(None, alias="public_description")
    owner_id: int | None = Field(None, alias="owner_id")
    deal_id: int | None = Field(None, alias="deal_id")
    lead_id: str | None = Field(None, alias="lead_id")
    org_id: int | None = Field(None, alias="org_id")
    person_id: int | None = Field(None, alias="person_id")
    project_id: int | None = Field(None, alias="project_id")


class AddLeadOptions(BaseModel):
    title: str | None = Field(None, alias="title")
    owner_id: int | None = Field(None, alias="owner_id")
    person_id: int | None = Field(None, alias="person_id")
    org_id: int | None = Field(None, alias="organization_id")


class AddNoteOptions(BaseModel):
    content: str | None = Field(None, alias="content")
    user_id: int | None = Field(None, alias="user_id")
    lead_id: str | None = Field(None, alias="lead_id")
    deal_id: int | None = Field(None, alias="deal_id")
    person_id: int | None = Field(None, alias="person_id")
    org_id: int | None = Field(None, alias="org_id")
    project_id: int | None = Field(None, alias="project_id")


class AddOrganizationOptions(BaseModel):
    name: str | None = Field(None, alias="name")
    owner_id: int | None = Field(None, alias="owner_id")


class AddPersonOptions(BaseModel):
    name: str | None = Field(None, alias="name")
    owner_id: int | None = Field(None, alias="owner_id")
    org_id: int | None = Field(None, alias="org_id")


class AddUserOptions(BaseModel):
    email: str | None = Field(None, alias="email")


class CreateDealOptions(BaseModel):
    title: str | None = Field(None, alias="title")
    value: float | None = Field(None, alias="value")
    owner_id: int | None = Field(None, alias="owner_id")
    person_id: int | None = Field(None, alias="person_id")
    org_id: int | None = Field(None, alias="org_id")
    currency: str | None = Field(None, alias="currency")
    pipeline_id: int | None = Field(None, alias="pipeline_id")
    stage_id: int | None = Field(None, alias="stage_id")


class ActivityService(Service):
    def add(self, options: AddActivityOptions) -> dict:
        return self._client.request(
            "POST",
            "api/v2/activities",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


    def delete(self, activity_id: str) -> dict:
        return self._client.request("DELETE", f"api/v2/activities/{activity_id}")


    def get_all(self) -> dict:
        return self._client.request("GET", "api/v2/activities")


class DealService(Service):
    def create(self, options: CreateDealOptions) -> dict:
        return self._client.request(
            "POST",
            "api/v2/deals",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )

    def delete(self, deal_id: str) -> dict:
        return self._client.request(
            "DELETE",
            f"api/v2/deals/{deal_id}",
        )


    def get_all(self) -> dict:
        return self._client.request("GET", "api/v2/deals")


class LeadService(Service):
    def add(self, options: AddLeadOptions) -> dict:
        return self._client.request(
            "POST",
            "api/v1/leads",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


    def delete(self, lead_id: str) -> dict:
        return self._client.request(
            "DELETE",
            f"api/v1/leads/{lead_id}",
        )


    def get_all(self) -> dict:
        return self._client.request("GET", "api/v1/leads")


class NoteService(Service):
    def add(self, options: AddNoteOptions) -> dict:
        return self._client.request(
            "POST",
            "api/v1/notes",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


    def delete(self, note_id: str) -> dict:
        return self._client.request("DELETE", f"api/v1/notes/{note_id}")


    def get_all(self) -> dict:
        return self._client.request("GET", "api/v1/notes")


class OrganizationService(Service):
    def add(self, options: AddOrganizationOptions) -> dict:
        return self._client.request(
            "POST",
            "api/v2/organizations",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


    def get_all(self) -> dict:
        return self._client.request("GET", "api/v2/organizations")


    def delete(self, organization_id: str) -> dict:
        return self._client.request("DELETE", f"api/v2/organizations/{organization_id}")


class PersonService(Service):
    def add(self, options: AddPersonOptions) -> dict:
        return self._client.request(
            "POST",
            "api/v2/persons",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )


    def get_all(self) -> dict:
        return self._client.request("GET", "api/v2/persons")


    def delete(self, person_id: str) -> dict:
        return self._client.request("DELETE", f"api/v2/persons/{person_id}")


class UserService(Service):
    def add(self, options: AddUserOptions) -> dict:
        return self._client.request(
            "POST",
            "api/v1/users",
            body=options.model_dump(exclude_none=True, by_alias=True),
        )

    def get_all(self) -> dict:
        return self._client.request("GET", "api/v1/users")
