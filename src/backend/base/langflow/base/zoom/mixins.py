import json
from abc import ABC, abstractmethod

from langflow.inputs.inputs import InputTypes

from .inputs import (
    INPUT_NAME_AUTH_TEXT,
)


class AuthTextMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def auth_text(self) -> dict | None:
        auth_text_input = self.get_input(INPUT_NAME_AUTH_TEXT)

        auth_text: dict | None = None
        if auth_text_input.value != "":
            auth_text = json.loads(auth_text_input.value)

        return auth_text
