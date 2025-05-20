from langflow.inputs import MessageTextInput

INPUT_NAME_AUTH_TEXT = "auth_text"


class AuthTextInput(MessageTextInput):
    name: str = INPUT_NAME_AUTH_TEXT
    display_name: str = "Text from Authentication component"
    info: str = "Text output from the Authentication component. JSON string with 'token' and 'api_url' keys."
    required: bool = True
