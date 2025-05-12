from pydantic import BaseModel, Field

from .client import FilterOp, Filters, SortOrder
from .inputs import (
    INPUT_INFO_FILTERS_COUNT,
    INPUT_INFO_FILTERS_FILTER_BY,
    INPUT_INFO_FILTERS_FILTER_OP,
    INPUT_INFO_FILTERS_FILTER_VALUE,
    INPUT_INFO_FILTERS_SORT_BY,
    INPUT_INFO_FILTERS_SORT_ORDER,
    INPUT_INFO_FILTERS_START_INDEX,
    INPUT_INFO_FILTERS_UPDATED_SINCE,
)


class FiltersSchema(BaseModel):
    count: int | None = Field(None, description=INPUT_INFO_FILTERS_COUNT)
    start_index: int | None = Field(None, description=INPUT_INFO_FILTERS_START_INDEX)
    sort_by: str | None = Field(None, description=INPUT_INFO_FILTERS_SORT_BY)
    sort_order: SortOrder | None = Field(None, description=INPUT_INFO_FILTERS_SORT_ORDER)
    filter_by: str | None = Field(None, description=INPUT_INFO_FILTERS_FILTER_BY)
    filter_op: FilterOp | None = Field(None, description=INPUT_INFO_FILTERS_FILTER_OP)
    filter_value: str | None = Field(None, description=INPUT_INFO_FILTERS_FILTER_VALUE)
    updated_since: str | None = Field(None, description=INPUT_INFO_FILTERS_UPDATED_SINCE)


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

class GatewayCredential(BaseModel):
    gateway_base_url: str
    origin: str
    auth_key: str
