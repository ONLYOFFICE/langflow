from langflow.inputs import MessageTextInput, SecretStrInput

INPUT_FORMAT_SORT_ORDER = "Can be 'ascending' or 'descending'."
INPUT_FORMAT_FILTER_OP = "Can be 'contains', 'equals', 'startsWith', or 'present'."
INPUT_FORMAT_FOLDER_IDS = "Can be a JSON array of IDs or a string of IDs separated by the separator."
INPUT_FORMAT_FILE_IDS = "Can be a JSON array of IDs or a string of IDs separated by the separator."

INPUT_NAME_AUTH_TEXT = "auth_text"
INPUT_NAME_ID_SEPARATOR = "id_separator"
INPUT_NAME_FOLDER_IDS = "folder_ids"
INPUT_NAME_FILE_IDS = "file_ids"
INPUT_NAME_FILTERS_COUNT = "filters_count"
INPUT_NAME_FILTERS_START_INDEX = "filters_start_index"
INPUT_NAME_FILTERS_SORT_BY = "filters_sort_by"
INPUT_NAME_FILTERS_SORT_ORDER = "filters_sort_order"
INPUT_NAME_FILTERS_FILTER_BY = "filters_filter_by"
INPUT_NAME_FILTERS_FILTER_OP = "filters_filter_op"
INPUT_NAME_FILTERS_FILTER_VALUE = "filters_filter_value"
INPUT_NAME_FILTERS_UPDATED_SINCE = "filters_updated_since"

INPUT_INFO_FILTERS_COUNT = "The number of items to return."
INPUT_INFO_FILTERS_START_INDEX = "The index of the first item to return."
INPUT_INFO_FILTERS_SORT_BY = "The field to sort by."
INPUT_INFO_FILTERS_SORT_ORDER = f"The sort order. {INPUT_FORMAT_SORT_ORDER}"
INPUT_INFO_FILTERS_FILTER_BY = "The field to filter by."
INPUT_INFO_FILTERS_FILTER_OP = f"The filter operation. {INPUT_FORMAT_FILTER_OP}"
INPUT_INFO_FILTERS_FILTER_VALUE = "The value to filter by."
INPUT_INFO_FILTERS_UPDATED_SINCE = "Only return items updated since this date."


class AuthTextInput(SecretStrInput):
    name: str = INPUT_NAME_AUTH_TEXT
    display_name: str = "Text from Basic Authentication"
    info: str = "Text output from the Basic Authentication component."
    advanced: bool = True


class IdSeparatorInput(MessageTextInput):
    name: str = INPUT_NAME_ID_SEPARATOR
    display_name: str = "ID Separator"
    info: str = "The separator used to split the IDs in the input string."
    advanced: bool = True


class RoomIdInput(MessageTextInput):
    name: str = "room_id"
    display_name: str = "Room ID"


class FolderIdInput(MessageTextInput):
    name: str = "folder_id"
    display_name: str = "Folder ID"


class FileIdInput(MessageTextInput):
    name: str = "file_id"
    display_name: str = "File ID"


class FolderIdsInput(MessageTextInput):
    name: str = INPUT_NAME_FOLDER_IDS
    display_name: str = "Folder IDs"


class FileIdsInput(MessageTextInput):
    name: str = INPUT_NAME_FILE_IDS
    display_name: str = "File IDs"


class DestFolderIdInput(MessageTextInput):
    name: str = "dest_folder_id"
    display_name: str = "Destination Folder ID"


class FiltersCountInput(MessageTextInput):
    name: str = INPUT_NAME_FILTERS_COUNT
    display_name: str = "Filters: Count"
    info: str = INPUT_INFO_FILTERS_COUNT
    advanced: bool = True


class FiltersStartIndexInput(MessageTextInput):
    name: str = INPUT_NAME_FILTERS_START_INDEX
    display_name: str = "Filters: Start Index"
    info: str = INPUT_INFO_FILTERS_START_INDEX
    advanced: bool = True


class FiltersSortByInput(MessageTextInput):
    name: str = INPUT_NAME_FILTERS_SORT_BY
    display_name: str = "Filters: Sort By"
    info: str = INPUT_INFO_FILTERS_SORT_BY
    advanced: bool = True


class FiltersSortOrderInput(MessageTextInput):
    name: str = INPUT_NAME_FILTERS_SORT_ORDER
    display_name: str = "Filters: Sort Order"
    info: str = INPUT_INFO_FILTERS_SORT_ORDER
    advanced: bool = True


class FiltersFilterByInput(MessageTextInput):
    name: str = INPUT_NAME_FILTERS_FILTER_BY
    display_name: str = "Filters: Filter By"
    info: str = INPUT_INFO_FILTERS_FILTER_BY
    advanced: bool = True


class FiltersFilterOpInput(MessageTextInput):
    name: str = INPUT_NAME_FILTERS_FILTER_OP
    display_name: str = "Filters: Filter Op"
    info: str = INPUT_INFO_FILTERS_FILTER_OP
    advanced: bool = True


class FiltersFilterValueInput(MessageTextInput):
    name: str = INPUT_NAME_FILTERS_FILTER_VALUE
    display_name: str = "Filters: Filter Value"
    info: str = INPUT_INFO_FILTERS_FILTER_VALUE
    advanced: bool = True


class FiltersUpdatedSinceInput(MessageTextInput):
    name: str = INPUT_NAME_FILTERS_UPDATED_SINCE
    display_name: str = "Filters: Updated Since"
    info: str = INPUT_INFO_FILTERS_UPDATED_SINCE
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
