from langflow.inputs import MessageTextInput, SecretStrInput

INPUT_DESCRIPTION_IS_PRIVATE = "Set to true to create a private channel."

INPUT_NAME_AUTH_TEXT = "auth_token"
INPUT_NAME_IS_PRIVATE = "is_private"


class AuthTextInput(SecretStrInput):
    name: str = INPUT_NAME_AUTH_TEXT
    display_name: str = "Bot User OAuth Token"
    info: str = "OAuth token for the Slack app."
    advanced: bool = True


class IsPrivateInput(MessageTextInput):
    name: str = INPUT_NAME_IS_PRIVATE
    display_name: str = "Is Private"
    info: str = INPUT_DESCRIPTION_IS_PRIVATE
    advanced: bool = True
