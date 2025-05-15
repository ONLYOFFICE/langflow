import json
from abc import ABC, abstractmethod

from langflow.inputs.inputs import InputTypes

from .inputs import (
    INPUT_NAME_AUTH_TEXT,
    INPUT_NAME_AUTO_APPROVE,
    INPUT_NAME_DURATION,
    INPUT_NAME_MEETING_ID,
    INPUT_NAME_RECURRENCE_END_TIMES,
    INPUT_NAME_RECURRENCE_TYPE,
    INPUT_NAME_SETTINGS,
    INPUT_NAME_TYPE,
)

BOOL_TRUE_VALUES = {"true", "1", "on", "yes", "y"}
BOOL_FALSE_VALUES = {"false", "0", "off", "no", "n"}


def to_bool(value: str) -> bool | None:
    if value in BOOL_TRUE_VALUES:
        return True
    if value in BOOL_FALSE_VALUES:
        return False
    return None


def to_dict(value: str) -> dict | None:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
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


class AutoApproveMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...

    @property
    def auto_approve(self) -> bool | None:
        auto_approve_input = self.get_input(INPUT_NAME_AUTO_APPROVE)
        return to_bool(auto_approve_input.value)


class DurationMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def duration(self) -> int | None:
        duration_input = self.get_input(INPUT_NAME_DURATION)
        return to_int(duration_input.value)


class MeetingIdMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...

    @property
    def meeting_id(self) -> int | None:
        meeting_id_input = self.get_input(INPUT_NAME_MEETING_ID)
        return to_int(meeting_id_input.value)


class RecurrenceEndTimesMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def recurrence_end_times(self) -> int | None:
        recurrence_end_times_input = self.get_input(INPUT_NAME_RECURRENCE_END_TIMES)
        return to_int(recurrence_end_times_input.value)


class RecurrenceTypeMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def recurrence_type(self) -> int | None:
        recurrence_type_input = self.get_input(INPUT_NAME_RECURRENCE_TYPE)
        return to_int(recurrence_type_input.value)


class SettingsMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...

    @property
    def settings(self) -> dict | None:
        settings_input = self.get_input(INPUT_NAME_SETTINGS)
        return to_dict(settings_input.value)


class TypeMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def type(self) -> int | None:
        type_input = self.get_input(INPUT_NAME_TYPE)
        return to_int(type_input.value)
