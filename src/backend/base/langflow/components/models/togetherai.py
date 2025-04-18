# from langchain_openai import ChatOpenAI
from langchain_together import ChatTogether
from pydantic.v1 import SecretStr

from langflow.base.models.model import LCModelComponent
#from langflow.base.models.openai_constants import OPENAI_MODEL_NAMES
from langflow.base.models.togetherai_constants import TOGETHERAI_MODEL_NAMES
from langflow.field_typing import LanguageModel
from langflow.field_typing.range_spec import RangeSpec
from langflow.inputs import BoolInput, DictInput, DropdownInput, IntInput, SecretStrInput, SliderInput, StrInput


class TogetherAIModelComponent(LCModelComponent):
    display_name = "TogetherAI"
    description = "Generates text using TogetherAI LLMs."
    icon = "TogetherAI"
    name = "TogetherAIModel"

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
        DropdownInput(
            name="model_name",
            display_name="Model Name",
            advanced=False,
            options=TOGETHERAI_MODEL_NAMES,
            value=TOGETHERAI_MODEL_NAMES[0],
        ),
        StrInput(
            name="togetherai_api_base",
            display_name="TogetherAI API Base",
            advanced=True,
            info="The base URL of the TogetherAI API. "
            "Defaults to https://api.together.xyz/v1. "
            "You can change this to use other APIs like JinaChat, LocalAI and Prem.",
        ),
        SecretStrInput(
            name="api_key",
            display_name="TogetherAI API Key",
            info="The TogetherAI API Key to use for the TogetherAI model.",
            advanced=False,
            value="TOGETHERAI_API_KEY",
            required=True,
        ),
        SliderInput(
            name="temperature", display_name="Temperature", value=0.1, range_spec=RangeSpec(min=0, max=1, step=0.01)
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
            info="The timeout for requests to TogetherAI completion API.",
            advanced=True,
            value=700,
        ),
    ]

    def build_model(self) -> LanguageModel:  # type: ignore[type-var]
        togetherai_api_key = self.api_key
        temperature = self.temperature
        model_name: str = self.model_name
        max_tokens = self.max_tokens
        model_kwargs = self.model_kwargs or {}
        togetherai_api_base = self.togetherai_api_base or "https://api.together.xyz/v1"
        json_mode = self.json_mode
        seed = self.seed
        max_retries = self.max_retries
        timeout = self.timeout

        api_key = SecretStr(togetherai_api_key).get_secret_value() if togetherai_api_key else None
        output = ChatTogether(
            max_tokens=max_tokens or None,
            model_kwargs=model_kwargs,
            model=model_name,
            base_url=togetherai_api_base,
            api_key=api_key,
            temperature=temperature if temperature is not None else 0.1,
            seed=seed,
            max_retries=max_retries,
            timeout=timeout,
        )
        if json_mode:
            output = output.bind(response_format={"type": "json_object"})

        return output

    def _get_exception_message(self, e: Exception):
        """Get a message from an TogetherAI exception.

        Args:
            e (Exception): The exception to get the message from.

        Returns:
            str: The message from the exception.
        """
        # try:
        #     from openai import BadRequestError
        # except ImportError:
        #     return None
        # if isinstance(e, BadRequestError):
        #     message = e.body.get("message")
        #     if message:
        #         return message
        return e
