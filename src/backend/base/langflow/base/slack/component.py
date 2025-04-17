from langflow.custom import Component as BaseComponent

from .client import Client
from .mixins import AuthTextMixin

_AUTH_KEY_VARIABLE_NAME = "slack_auth_key"

class Component(BaseComponent, AuthTextMixin):
    display_name = "Slack Component"
    description = "Component to interact with Slack."
    icon = "slack"


    async def _get_client(self) -> Client:
        client = Client()
        if self.auth_token:
            client.auth = self.auth_token
        else:
            try:
                key = await self.get_variables(_AUTH_KEY_VARIABLE_NAME, "")
            except:  # noqa: E722
                key = None

            if not key:
                msg = f"{_AUTH_KEY_VARIABLE_NAME} LangFlow variable is not set"
                raise ValueError(msg)

            client.auth = key

        return client
