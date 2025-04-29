from langflow.inputs import MessageTextInput, SecretStrInput

INPUT_DESCRIPTION_FORCE = "Continue inviting the valid ones while disregarding invalid IDs."
INPUT_DESCRIPTION_INCLUDE_ALL_METADATA = "Return all metadata associated with this message."
INPUT_DESCRIPTION_INCLUSIVE = "Include messages with oldest or latest timestamps in results."
INPUT_DESCRIPTION_IS_PRIVATE = "Create a private channel instead of a public one."
INPUT_DESCRIPTION_LIMIT = "The maximum number of items to return."

INPUT_NAME_OAUTH_TOKEN = "oauth_token"
INPUT_NAME_FORCE = "force"
INPUT_NAME_INCLUDE_ALL_METADATA = "include_all_metadata"
INPUT_NAME_INCLUSIVE = "inclusive"
INPUT_NAME_IS_PRIVATE = "is_private"
INPUT_NAME_LIMIT = "limit"


class OAuthTokenInput(SecretStrInput):
    name: str = INPUT_NAME_OAUTH_TOKEN
    display_name: str = "Bot User OAuth Token"
    info: str = "OAuth token for the Slack app."
    required: bool = True


class ForceInput(MessageTextInput):
    name: str = INPUT_NAME_FORCE
    display_name: str = "Force"
    info: str = INPUT_DESCRIPTION_FORCE
    advanced: bool = True


class IncludeAllMetadataInput(MessageTextInput):
    name: str = INPUT_NAME_INCLUDE_ALL_METADATA
    display_name: str = "Include All Metadata"
    info: str = INPUT_DESCRIPTION_INCLUDE_ALL_METADATA
    advanced: bool = True


class InclusiveInput(MessageTextInput):
    name: str = INPUT_NAME_INCLUSIVE
    display_name: str = "Inclusive"
    info: str = INPUT_DESCRIPTION_INCLUSIVE
    advanced: bool = True


class IsPrivateInput(MessageTextInput):
    name: str = INPUT_NAME_IS_PRIVATE
    display_name: str = "Is Private"
    info: str = INPUT_DESCRIPTION_IS_PRIVATE
    advanced: bool = True


class LimitInput(MessageTextInput):
    name: str = INPUT_NAME_LIMIT
    display_name: str = "Limit"
    info: str = INPUT_DESCRIPTION_LIMIT
    advanced: bool = True
