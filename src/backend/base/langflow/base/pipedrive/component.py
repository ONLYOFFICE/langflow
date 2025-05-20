from langflow.custom import Component as BaseComponent

from .client import Client
from .mixins import AuthTextMixin


class Component(BaseComponent, AuthTextMixin):
    display_name = "Pipedrive Component"
    description = "Component to interact with Pipedrive."
    icon = "pipedrive"


    def _get_client(self) -> Client:
        client = Client()

        if self.auth_text:
            client.auth_text = self.auth_text

        return client
