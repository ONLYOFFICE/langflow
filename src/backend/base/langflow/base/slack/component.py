from langflow.custom import Component as BaseComponent

from .client import Client
from .mixins import OAuthTokenMixin


class Component(BaseComponent, OAuthTokenMixin):
    display_name = "Slack Component"
    description = "Component to interact with Slack."
    icon = "slack"


    def _get_client(self) -> Client:
        client = Client()

        if self.auth_token:
            client.auth = self.auth_token

        return client
