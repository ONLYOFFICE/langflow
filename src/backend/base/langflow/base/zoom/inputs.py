from langflow.inputs import MessageTextInput

DESCRIPTION_AUTO_APPROVE = "If a meeting was scheduled with the 'approval_type' field value of 1 (manual approval) but you want to automatically approve meeting registrants, set the value of this field to true."  # noqa: E501
DESCRIPTION_DURATION = "The meeting's scheduled duration, in minutes. This field is only used for scheduled meetings (2)."  # noqa: E501
DESCRIPTION_MEETING_ID = "The meeting ID."
DESCRIPTION_RECURRENCE_END_TIMES = "Select how many times the meeting should recur before it is canceled. If 'end_times' is set to 0, it means there is no end time. The maximum number of recurring is 60. Cannot be used with 'end_date_time'."  # noqa: E501
DESCRIPTION_RECURRENCE_TYPE = "REQUIRED with meeting type 8. Recurrence meeting types.\n1 - Daily.\n2 - Weekly.\n3 - Monthly."  # noqa: E501
DESCRIPTION_SETTINGS = "Information about the meeting's settings in JSON string format."
DESCRIPTION_TYPE = "The type of meeting.\n1 - An instant meeting.\n2 - A scheduled meeting.\n3 - A recurring meeting with no fixed time.\n8 - A recurring meeting with fixed time.\n10 - A screen share only meeting."  # noqa: E501

INPUT_NAME_AUTH_TEXT = "auth_text"
INPUT_NAME_AUTO_APPROVE = "auto_approve"
INPUT_NAME_DURATION = "duration"
INPUT_NAME_MEETING_ID = "meeting_id"
INPUT_NAME_RECURRENCE_END_TIMES = "recurrence_end_times"
INPUT_NAME_RECURRENCE_TYPE = "recurrence_type"
INPUT_NAME_SETTINGS = "settings"
INPUT_NAME_TYPE = "type"


class AuthTextInput(MessageTextInput):
    name: str = INPUT_NAME_AUTH_TEXT
    display_name: str = "Text from Basic Authentication"
    info: str = "Text output from the Basic Authentication component."
    required: bool = True


class AutoApproveInput(MessageTextInput):
    name: str = INPUT_NAME_AUTO_APPROVE
    display_name: str = "Auto Approve"
    info: str = "Auto approve the registrant."
    advanced: bool = True


class DurationInput(MessageTextInput):
    name: str = INPUT_NAME_DURATION
    display_name: str = "Duration"
    info: str = DESCRIPTION_DURATION
    advanced: bool = True


class MeetingIdInput(MessageTextInput):
    name: str = INPUT_NAME_MEETING_ID
    display_name: str = "Meeting ID"
    info: str = DESCRIPTION_MEETING_ID


class RecurrenceEndTimesInput(MessageTextInput):
    name: str = INPUT_NAME_RECURRENCE_END_TIMES
    display_name: str = "Recurrence End Times"
    info: str = DESCRIPTION_RECURRENCE_END_TIMES
    advanced: bool = True


class RecurrenceTypeInput(MessageTextInput):
    name: str = INPUT_NAME_RECURRENCE_TYPE
    display_name: str = "Recurrence Type"
    info: str = DESCRIPTION_RECURRENCE_TYPE
    advanced: bool = True


class SettingsInput(MessageTextInput):
    name: str = INPUT_NAME_SETTINGS
    display_name: str = "Settings"
    info: str = DESCRIPTION_SETTINGS
    advanced: bool = True


class TypeInput(MessageTextInput):
    name: str = INPUT_NAME_TYPE
    display_name: str = "Type"
    info: str = DESCRIPTION_TYPE
