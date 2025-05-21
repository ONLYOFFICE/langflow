import os

from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from langflow.base.models.model import LCModelComponent
from langflow.field_typing import LanguageModel
from langflow.field_typing.range_spec import RangeSpec
from langflow.inputs import BoolInput, DictInput, IntInput, MessageTextInput, SliderInput
from langflow.inputs.inputs import SecretStrInput


class DocSpaceModelComponent(LCModelComponent):
    display_name = "DocSpaceAI"
    description = "Generates text using DocSpace LLMs."
    icon = "onlyoffice"
    name = "DocSpaceAIModel"

    inputs = [
        MessageTextInput(
            name="portal_url",
            display_name="Portal URL",
            info="DocSpace portal URL.",
            required=True,
        ),
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            info="The API key to use for the DocSpace AI model.",
            required=True,
        ),
        *LCModelComponent._base_inputs,
        IntInput(
            name="max_tokens",
            display_name="Max Tokens",
            advanced=True,
            info="The maximum number of tokens to generate. Set to 0 for unlimited tokens.",
            range_spec=RangeSpec(min=0, max=128000),
        ),
        DictInput(
            name="model_kwargs",
            display_name="Model Kwargs",
            advanced=True,
            info="Additional keyword arguments to pass to the model.",
        ),
        BoolInput(
            name="json_mode",
            display_name="JSON Mode",
            advanced=True,
            info="If True, it will output JSON regardless of passing a schema.",
        ),
        MessageTextInput(
            name="model_name",
            display_name="Model Name",
            advanced=False,
            info="The name of the DocSpace AI model to use.",
            required=True,
        ),
        SliderInput(
            name="temperature",
            display_name="Temperature",
            value=0.1,
            range_spec=RangeSpec(min=0, max=1, step=0.01),
            show=True,
        ),
        IntInput(
            name="seed",
            display_name="Seed",
            info="The seed controls the reproducibility of the job.",
            advanced=True,
            value=1,
        ),
        IntInput(
            name="max_retries",
            display_name="Max Retries",
            info="The maximum number of retries to make when generating.",
            advanced=True,
            value=5,
        ),
        IntInput(
            name="timeout",
            display_name="Timeout",
            info="The timeout for requests to DocSpace AI completion API.",
            advanced=True,
            value=700,
        )
    ]

    def build_model(self) -> LanguageModel:  # type: ignore[type-var]
        base_url = os.environ.get("AI_GATEWAY_BASE_URL")
        if not base_url:
            msg = "AI_GATEWAY_BASE_URL environment variable not set"
            raise ValueError(msg)

        parameters = {
            "api_key": SecretStr("docspace"),
            "model_name": self.model_name,
            "max_tokens": self.max_tokens or None,
            "model_kwargs": self.model_kwargs or {},
            "base_url": base_url,
            "seed": self.seed,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "temperature": self.temperature if self.temperature is not None else 0.1,
            "default_headers": {
                "origin": self.portal_url,
                "cookie": f"asc_auth_key={self.api_key};"
            }
        }

        output = ChatOpenAI(**parameters)
        if self.json_mode:
            output = output.bind(response_format={"type": "json_object"})

        return output

    def _get_exception_message(self, e: Exception):
        """Get a message from an OpenAI exception.

        Args:
            e (Exception): The exception to get the message from.

        Returns:
            str: The message from the exception.
        """
        try:
            from openai import BadRequestError
        except ImportError:
            return None
        if isinstance(e, BadRequestError):
            message = e.body.get("message")
            if message:
                return message
        return None
