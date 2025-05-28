import json
from abc import ABC, abstractmethod

from langflow.inputs.inputs import InputTypes

from .inputs import (
    INPUT_NAME_AUTH_TEXT,
    INPUT_NAME_DEAL_ID,
    INPUT_NAME_ORG_ID,
    INPUT_NAME_OWNER_ID,
    INPUT_NAME_PERSON_ID,
    INPUT_NAME_PINNED,
    INPUT_NAME_PIPELINE_ID,
    INPUT_NAME_PROJECT_ID,
    INPUT_NAME_STAGE_ID,
    INPUT_NAME_USER_ID,
    INPUT_NAME_VALUE,
)

BOOL_TRUE_VALUES = {"true", "1", "on", "yes", "y"}
BOOL_FALSE_VALUES = {"false", "0", "off", "no", "n"}


def to_bool(value: str) -> bool | None:
    if value in BOOL_TRUE_VALUES:
        return True
    if value in BOOL_FALSE_VALUES:
        return False
    return None


def to_float(value: str) -> float | None:
    if value.strip().isdigit():
        return float(value)
    return None


def to_int(value: str) -> int | None:
    if value.strip().isdigit():
        return int(value)
    return None


class AuthTextMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def auth_text(self) -> dict | None:
        auth_text_input = self.get_input(INPUT_NAME_AUTH_TEXT)

        auth_text: dict | None = None
        if auth_text_input.value != "":
            auth_text = json.loads(auth_text_input.value)

        return auth_text


class DealIdMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def deal_id(self) -> int | None:
        deal_id_input = self.get_input(INPUT_NAME_DEAL_ID)

        return to_int(deal_id_input.value)


class OrgIdMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def org_id(self) -> int | None:
        org_id_input = self.get_input(INPUT_NAME_ORG_ID)

        return to_int(org_id_input.value)


class OwnerIdMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def owner_id(self) -> int | None:
        owner_id_input = self.get_input(INPUT_NAME_OWNER_ID)

        return to_int(owner_id_input.value)


class PersonIdMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def person_id(self) -> int | None:
        person_id_input = self.get_input(INPUT_NAME_PERSON_ID)

        return to_int(person_id_input.value)


class PinnedMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def pinned(self) -> bool | None:
        pinned_input = self.get_input(INPUT_NAME_PINNED)

        return to_bool(pinned_input.value)


class PipelineIdMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def pipeline_id(self) -> int | None:
        pipeline_id_input = self.get_input(INPUT_NAME_PIPELINE_ID)

        return to_int(pipeline_id_input.value)


class ProjectIdMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def project_id(self) -> int | None:
        project_id_input = self.get_input(INPUT_NAME_PROJECT_ID)

        return to_int(project_id_input.value)


class StageIdMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def stage_id(self) -> int | None:
        stage_id_input = self.get_input(INPUT_NAME_STAGE_ID)

        return to_int(stage_id_input.value)


class UserIdMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def pipedrive_user_id(self) -> int | None:
        user_id_input = self.get_input(INPUT_NAME_USER_ID)

        return to_int(user_id_input.value)


class ValueMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def deal_value(self) -> int | None:
        value_input = self.get_input(INPUT_NAME_VALUE)

        return to_float(value_input.value)
