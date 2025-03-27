from typing import Protocol, Self

from pydantic import BaseModel, Field

from langflow.inputs.inputs import InputTypes

from .client import FilterOp, Filters, SortOrder
from .inputs import (
    FILTERS_DESCRIPTION_COUNT_INPUT,
    FILTERS_DESCRIPTION_FILTER_BY_INPUT,
    FILTERS_DESCRIPTION_FILTER_OP_INPUT,
    FILTERS_DESCRIPTION_FILTER_VALUE_INPUT,
    FILTERS_DESCRIPTION_SORT_BY_INPUT,
    FILTERS_DESCRIPTION_SORT_ORDER_INPUT,
    FILTERS_DESCRIPTION_START_INDEX_INPUT,
    FILTERS_DESCRIPTION_UPDATED_SINCE_INPUT,
    FILTERS_NAME_COUNT_INPUT,
    FILTERS_NAME_FILTER_BY_INPUT,
    FILTERS_NAME_FILTER_OP_INPUT,
    FILTERS_NAME_FILTER_VALUE_INPUT,
    FILTERS_NAME_SORT_BY_INPUT,
    FILTERS_NAME_SORT_ORDER_INPUT,
    FILTERS_NAME_START_INDEX_INPUT,
    FILTERS_NAME_UPDATED_SINCE_INPUT,
)


class Component(Protocol):
    def get_input(self, name: str) -> InputTypes:
        ...


class FiltersSchema(BaseModel):
    count: int | None = Field(None, description=FILTERS_DESCRIPTION_COUNT_INPUT)
    start_index: int | None = Field(None, description=FILTERS_DESCRIPTION_START_INDEX_INPUT)
    sort_by: str | None = Field(None, description=FILTERS_DESCRIPTION_SORT_BY_INPUT)
    sort_order: SortOrder | None = Field(None, description=FILTERS_DESCRIPTION_SORT_ORDER_INPUT)
    filter_by: str | None = Field(None, description=FILTERS_DESCRIPTION_FILTER_BY_INPUT)
    filter_op: FilterOp | None = Field(None, description=FILTERS_DESCRIPTION_FILTER_OP_INPUT)
    filter_value: str | None = Field(None, description=FILTERS_DESCRIPTION_FILTER_VALUE_INPUT)
    updated_since: str | None = Field(None, description=FILTERS_DESCRIPTION_UPDATED_SINCE_INPUT)


    @classmethod
    def from_component(cls, component: Component) -> Self:
        count_input = component.get_input(FILTERS_NAME_COUNT_INPUT)
        start_index_input = component.get_input(FILTERS_NAME_START_INDEX_INPUT)
        sort_by_input = component.get_input(FILTERS_NAME_SORT_BY_INPUT)
        sort_order_input = component.get_input(FILTERS_NAME_SORT_ORDER_INPUT)
        filter_by_input = component.get_input(FILTERS_NAME_FILTER_BY_INPUT)
        filter_op_input = component.get_input(FILTERS_NAME_FILTER_OP_INPUT)
        filter_value_input = component.get_input(FILTERS_NAME_FILTER_VALUE_INPUT)
        updated_since_input = component.get_input(FILTERS_NAME_UPDATED_SINCE_INPUT)

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

        return cls(
            count=count,
            start_index=start_index,
            sort_by=sort_by,
            sort_order=sort_order,
            filter_by=filter_by,
            filter_op=filter_op,
            filter_value=filter_value,
            updated_since=updated_since,
        )


    def to_filters(self) -> Filters:
        return Filters(
            count=self.count,
            start_index=self.start_index,
            sort_by=self.sort_by,
            sort_order=self.sort_order,
            filter_by=self.filter_by,
            filter_op=self.filter_op,
            filter_value=self.filter_value,
            updated_since=self.updated_since,
        )
