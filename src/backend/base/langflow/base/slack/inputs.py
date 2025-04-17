from langflow.inputs import SecretStrInput

INPUT_NAME_AUTH_TEXT = "auth_token"


class AuthTextInput(SecretStrInput):
    name: str = INPUT_NAME_AUTH_TEXT
    display_name: str = "Bot User OAuth Token"
    info: str = "OAuth token for the Slack app."
    advanced: bool = True
