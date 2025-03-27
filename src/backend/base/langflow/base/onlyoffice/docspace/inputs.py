from langflow.inputs import MessageTextInput

FILTERS_NAME_COUNT_INPUT = "filters_count"
FILTERS_NAME_START_INDEX_INPUT = "filters_start_index"
FILTERS_NAME_SORT_BY_INPUT = "filters_sort_by"
FILTERS_NAME_SORT_ORDER_INPUT = "filters_sort_order"
FILTERS_NAME_FILTER_BY_INPUT = "filters_filter_by"
FILTERS_NAME_FILTER_OP_INPUT = "filters_filter_op"
FILTERS_NAME_FILTER_VALUE_INPUT = "filters_filter_value"
FILTERS_NAME_UPDATED_SINCE_INPUT = "filters_updated_since"

FILTERS_DESCRIPTION_COUNT_INPUT = "The number of items to return."
FILTERS_DESCRIPTION_START_INDEX_INPUT = "The index of the first item to return."
FILTERS_DESCRIPTION_SORT_BY_INPUT = "The field to sort by."
FILTERS_DESCRIPTION_SORT_ORDER_INPUT = "The sort order."
FILTERS_DESCRIPTION_FILTER_BY_INPUT = "The field to filter by."
FILTERS_DESCRIPTION_FILTER_OP_INPUT = "The filter operation."
FILTERS_DESCRIPTION_FILTER_VALUE_INPUT = "The value to filter by."
FILTERS_DESCRIPTION_UPDATED_SINCE_INPUT = "Only return items updated since this date."


class FiltersCountInput(MessageTextInput):
    name: str = FILTERS_NAME_COUNT_INPUT
    display_name: str = "Filters: Count"
    info: str = FILTERS_DESCRIPTION_COUNT_INPUT
    advanced: bool = True


class FiltersStartIndexInput(MessageTextInput):
    name: str = FILTERS_NAME_START_INDEX_INPUT
    display_name: str = "Filters: Start Index"
    info: str = FILTERS_DESCRIPTION_START_INDEX_INPUT
    advanced: bool = True


class FiltersSortByInput(MessageTextInput):
    name: str = FILTERS_NAME_SORT_BY_INPUT
    display_name: str = "Filters: Sort By"
    info: str = FILTERS_DESCRIPTION_SORT_BY_INPUT
    advanced: bool = True


class FiltersSortOrderInput(MessageTextInput):
    name: str = FILTERS_NAME_SORT_ORDER_INPUT
    display_name: str = "Filters: Sort Order"
    info: str = f"{FILTERS_DESCRIPTION_SORT_ORDER_INPUT} Can be 'ascending' or 'descending'."
    advanced: bool = True


class FiltersFilterByInput(MessageTextInput):
    name: str = FILTERS_NAME_FILTER_BY_INPUT
    display_name: str = "Filters: Filter By"
    info: str = FILTERS_DESCRIPTION_FILTER_BY_INPUT
    advanced: bool = True


class FiltersFilterOpInput(MessageTextInput):
    name: str = FILTERS_NAME_FILTER_OP_INPUT
    display_name: str = "Filters: Filter Op"
    info: str = f"{FILTERS_DESCRIPTION_FILTER_OP_INPUT} Can be 'contains', 'equals', 'startsWith', or 'present'."
    advanced: bool = True


class FiltersFilterValueInput(MessageTextInput):
    name: str = FILTERS_NAME_FILTER_VALUE_INPUT
    display_name: str = "Filters: Filter Value"
    info: str = FILTERS_DESCRIPTION_FILTER_VALUE_INPUT
    advanced: bool = True


class FiltersUpdatedSinceInput(MessageTextInput):
    name: str = FILTERS_NAME_UPDATED_SINCE_INPUT
    display_name: str = "Filters: Updated Since"
    info: str = FILTERS_DESCRIPTION_UPDATED_SINCE_INPUT
    advanced: bool = True


def filters_inputs() -> list[MessageTextInput]:
    return [
        FiltersCountInput(),
        FiltersStartIndexInput(),
        FiltersSortByInput(),
        FiltersSortOrderInput(),
        FiltersFilterByInput(),
        FiltersFilterOpInput(),
        FiltersFilterValueInput(),
        FiltersUpdatedSinceInput(),
    ]
