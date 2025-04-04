from typing import Literal

from pydantic import BaseModel, Field

SortOrder = Literal["ascending", "descending"]
FilterOp = Literal["contains", "equals", "startsWith", "present"]


class Filters(BaseModel):
    count: int | None = Field(None, alias="count")
    start_index: int | None = Field(None, alias="startIndex")
    sort_by: str | None = Field(None, alias="sortBy")
    sort_order: SortOrder | None = Field(None, alias="sortOrder")
    filter_by: str | None = Field(None, alias="filterBy")
    filter_op: FilterOp | None = Field(None, alias="filterOp")
    filter_value: str | None = Field(None, alias="filterValue")
    updated_since: str | None = Field(None, alias="updatedSince")
