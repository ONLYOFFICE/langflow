from abc import ABC, abstractmethod

from langflow.inputs.inputs import InputTypes

from .inputs import INPUT_NAME_AUTH_TEXT


class AuthTextMixin(ABC):
    @abstractmethod
    def get_input(self, name: str) -> InputTypes:
        ...


    @property
    def auth_token(self) -> str | None:
        auth_text_input = self.get_input(INPUT_NAME_AUTH_TEXT)

        return auth_text_input.value if auth_text_input.value != "" else None
