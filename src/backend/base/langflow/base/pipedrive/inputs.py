from langflow.inputs import MessageTextInput

INPUT_NAME_AUTH_TEXT = "auth_text"
INPUT_NAME_DEAL_ID = "deal_id"
INPUT_NAME_ORG_ID = "org_id"
INPUT_NAME_OWNER_ID = "owner_id"
INPUT_NAME_PINNED = "pinned"
INPUT_NAME_PERSON_ID = "person_id"
INPUT_NAME_PIPELINE_ID = "pipeline_id"
INPUT_NAME_PROJECT_ID = "project_id"
INPUT_NAME_STAGE_ID = "stage_id"
INPUT_NAME_USER_ID = "pipedrive_user_id"
INPUT_NAME_VALUE = "deal_value"


class AuthTextInput(MessageTextInput):
    name: str = INPUT_NAME_AUTH_TEXT
    display_name: str = "Text from Authentication component"
    info: str = "Text output from the Authentication component. JSON string with 'token' and 'api_url' keys."
    required: bool = True


class DealIdInput(MessageTextInput):
    name: str = INPUT_NAME_DEAL_ID
    display_name: str = "Deal ID"


class OrgIdInput(MessageTextInput):
    name: str = INPUT_NAME_ORG_ID
    display_name: str = "Organization ID"


class OwnerIdInput(MessageTextInput):
    name: str = INPUT_NAME_OWNER_ID
    display_name: str = "Owner ID"


class PersonIdInput(MessageTextInput):
    name: str = INPUT_NAME_PERSON_ID
    display_name: str = "Person ID"


class PinnedInput(MessageTextInput):
    name: str = INPUT_NAME_PINNED
    display_name: str = "Pinned"


class PipelineIdInput(MessageTextInput):
    name: str = INPUT_NAME_PIPELINE_ID
    display_name: str = "Pipeline ID"


class ProjectIdInput(MessageTextInput):
    name: str = INPUT_NAME_PROJECT_ID
    display_name: str = "Project ID"


class StageIdInput(MessageTextInput):
    name: str = INPUT_NAME_STAGE_ID
    display_name: str = "Stage ID"


class UserIdInput(MessageTextInput):
    name: str = INPUT_NAME_USER_ID
    display_name: str = "User ID"


class ValueInput(MessageTextInput):
    name: str = INPUT_NAME_VALUE
    display_name: str = "Value"
