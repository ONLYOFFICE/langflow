import json
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from langflow.inputs.inputs import InputTypes

from .inputs import (
    INPUT_NAME_AUTH_TEXT,
    INPUT_NAME_FILE_IDS,
    INPUT_NAME_FILTERS_COUNT,
    INPUT_NAME_FILTERS_FILTER_BY,
    INPUT_NAME_FILTERS_FILTER_OP,
    INPUT_NAME_FILTERS_FILTER_VALUE,
    INPUT_NAME_FILTERS_SORT_BY,
    INPUT_NAME_FILTERS_SORT_ORDER,
    INPUT_NAME_FILTERS_START_INDEX,
    INPUT_NAME_FILTERS_UPDATED_SINCE,
    INPUT_NAME_FOLDER_IDS,
    INPUT_NAME_ID_SEPARATOR,
)
from .schemas import FiltersSchema

if TYPE_CHECKING:
    from .client import FilterOp, SortOrder


BOOL_TRUE_VALUES = {"true", "1", "on", "yes", "y"}
BOOL_FALSE_VALUES = {"false", "0", "off", "no", "n"}


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


class IdSeparatorMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def id_separator(self) -> str | None:
        id_separator_input = self.get_input(INPUT_NAME_ID_SEPARATOR)

        id_separator: str | None = None
        if id_separator_input.value != "":
            id_separator = id_separator_input.value

        return id_separator


class FolderIdsMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    @abstractmethod
    def id_separator(self) -> str | None:
        ...


    @property
    def folder_ids(self) -> list[int | str] | None:
        folder_ids_input = self.get_input(INPUT_NAME_FOLDER_IDS)

        folder_ids: list[int | str] | None = None
        if folder_ids_input.value != "":
            if self.id_separator:
                folder_ids = [
                    folder_id.strip() if not folder_id.strip().isdigit() else int(folder_id.strip())
                    for folder_id in folder_ids_input.value.split(self.id_separator)
                ]
            else:
                folder_ids = json.loads(folder_ids_input.value)

        return folder_ids


class FileIdsMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    @abstractmethod
    def id_separator(self) -> str | None:
        ...


    @property
    def file_ids(self) -> list[int | str] | None:
        file_ids_input = self.get_input(INPUT_NAME_FILE_IDS)

        file_ids: list[int | str] | None = None
        if file_ids_input.value != "":
            if self.id_separator:
                file_ids = [
                    file_id.strip() if not file_id.strip().isdigit() else int(file_id.strip())
                    for file_id in file_ids_input.value.split(self.id_separator)
                ]
            else:
                file_ids = json.loads(file_ids_input.value)

        return file_ids


class BooleanMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...

    def boolean(self, name: str) -> bool | None:
        boolean_input = self.get_input(name)

        if boolean_input.value == "":
            return None
        if boolean_input.value in BOOL_TRUE_VALUES:
            return True
        if boolean_input.value in BOOL_FALSE_VALUES:
            return False

        return None


class FiltersMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def filters(self) -> FiltersSchema:
        count_input = self.get_input(INPUT_NAME_FILTERS_COUNT)
        start_index_input = self.get_input(INPUT_NAME_FILTERS_START_INDEX)
        sort_by_input = self.get_input(INPUT_NAME_FILTERS_SORT_BY)
        sort_order_input = self.get_input(INPUT_NAME_FILTERS_SORT_ORDER)
        filter_by_input = self.get_input(INPUT_NAME_FILTERS_FILTER_BY)
        filter_op_input = self.get_input(INPUT_NAME_FILTERS_FILTER_OP)
        filter_value_input = self.get_input(INPUT_NAME_FILTERS_FILTER_VALUE)
        updated_since_input = self.get_input(INPUT_NAME_FILTERS_UPDATED_SINCE)

        count: int | None = None
        if count_input.value != "":
            count = int(count_input.value)

        start_index: int | None = None
        if start_index_input.value != "":
            start_index = int(start_index_input.value)

        sort_by: str | None = None
        if sort_by_input.value != "":
            sort_by = sort_by_input.value

        sort_order: SortOrder | None = None
        if sort_order_input.value != "":
            sort_order = sort_order_input.value

        filter_by: str | None = None
        if filter_by_input.value != "":
            filter_by = filter_by_input.value

        filter_op: FilterOp | None = None
        if filter_op_input.value != "":
            filter_op = filter_op_input.value

        filter_value: str | None = None
        if filter_value_input.value != "":
            filter_value = filter_value_input.value

        updated_since: str | None = None
        if updated_since_input.value != "":
            updated_since = updated_since_input.value

        return FiltersSchema(
            count=count,
            start_index=start_index,
            sort_by=sort_by,
            sort_order=sort_order,
            filter_by=filter_by,
            filter_op=filter_op,
            filter_value=filter_value,
            updated_since=updated_since,
        )
