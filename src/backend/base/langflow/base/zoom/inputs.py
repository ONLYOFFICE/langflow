from langflow.inputs import MessageTextInput

INPUT_NAME_AUTH_TEXT = "auth_text"


class AuthTextInput(MessageTextInput):
    name: str = INPUT_NAME_AUTH_TEXT
    display_name: str = "Text from Basic Authentication"
    info: str = "Text output from the Basic Authentication component."
    required: bool = True
