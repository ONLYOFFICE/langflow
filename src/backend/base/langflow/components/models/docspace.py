from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from langflow.base.models.model import LCModelComponent
from langflow.base.onlyoffice.docspace import AICredentialMixin
from langflow.field_typing import LanguageModel
from langflow.field_typing.range_spec import RangeSpec
from langflow.inputs import BoolInput, DictInput, IntInput, MessageTextInput, SliderInput
from langflow.logging import logger
from langflow.utils.async_helpers import run_until_complete


class DocSpaceModelComponent(LCModelComponent, AICredentialMixin):
    display_name = "DocSpaceAI"
    description = "Generates text using DocSpace LLMs."
    icon = "onlyoffice"
    name = "DocSpaceAIModel"

    inputs = [
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
        credential = run_until_complete(self.get_gateway_credential(self.get_variables))

        parameters = {
            "api_key": SecretStr("docspace"),
            "model_name": self.model_name,
            "max_tokens": self.max_tokens or None,
            "model_kwargs": self.model_kwargs or {},
            "base_url": credential.gateway_base_url,
            "seed": self.seed,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "temperature": self.temperature if self.temperature is not None else 0.1,
            "default_headers": {
                "origin": credential.origin,
                "cookie": f"asc_auth_key={credential.auth_key};"
            }
        }

        logger.info(f"Model name: {self.model_name}")
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
