from abc import ABC, abstractmethod

from langflow.inputs.inputs import InputTypes

from .inputs import (
    INPUT_NAME_AUTH_TEXT,
    INPUT_NAME_FORCE,
    INPUT_NAME_INCLUDE_ALL_METADATA,
    INPUT_NAME_INCLUSIVE,
    INPUT_NAME_IS_PRIVATE,
    INPUT_NAME_LIMIT,
)

BOOL_TRUE_VALUES = {"true", "1", "on", "yes", "y"}
BOOL_FALSE_VALUES = {"false", "0", "off", "no", "n"}


def to_bool(value: str) -> bool | None:
    if value in BOOL_TRUE_VALUES:
        return True
    if value in BOOL_FALSE_VALUES:
        return False
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
    def auth_token(self) -> str | None:
        auth_text_input = self.get_input(INPUT_NAME_AUTH_TEXT)

        return auth_text_input.value if auth_text_input.value != "" else None


class ForceMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def force(self) -> bool | None:
        boolean_input = self.get_input(INPUT_NAME_FORCE)

        return to_bool(boolean_input.value)


class IncludeAllMetadataMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def include_all_metadata(self) -> bool | None:
        boolean_input = self.get_input(INPUT_NAME_INCLUDE_ALL_METADATA)

        return to_bool(boolean_input.value)


class InclusiveMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def inclusive(self) -> bool | None:
        boolean_input = self.get_input(INPUT_NAME_INCLUSIVE)

        return to_bool(boolean_input.value)


class IsPrivateMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def is_private(self) -> bool | None:
        boolean_input = self.get_input(INPUT_NAME_IS_PRIVATE)

        return to_bool(boolean_input.value)


class LimitMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def limit(self) -> int | None:
        integer_input = self.get_input(INPUT_NAME_LIMIT)

        return to_int(integer_input.value)
