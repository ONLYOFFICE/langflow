import os

from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr

from langflow.base.embeddings.model import LCEmbeddingsModel
from langflow.field_typing import Embeddings
from langflow.inputs import BoolInput, DictInput, FloatInput, IntInput, MessageTextInput
from langflow.inputs.inputs import SecretStrInput


class DocSpaceEmbeddingsComponent(LCEmbeddingsModel):
    display_name = "DocSpaceAI Embeddings"
    description = "Generate embeddings using DocSpace models."
    icon = "onlyoffice"
    name = "DocSpaceAIEmbeddings"

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
        IntInput(name="chunk_size", display_name="Chunk Size", advanced=True, value=1000),
        IntInput(name="embedding_ctx_length", display_name="Embedding Context Length", advanced=True, value=1536),
        IntInput(name="max_retries", display_name="Max Retries", value=3, advanced=True),
        MessageTextInput(
            name="model",
            display_name="Model",
            advanced=False,
            required=True
        ),
        DictInput(name="model_kwargs", display_name="Model Kwargs", advanced=True),
        FloatInput(name="request_timeout", display_name="Request Timeout", advanced=True),
        BoolInput(name="show_progress_bar", display_name="Show Progress Bar", advanced=True),
        BoolInput(name="skip_empty", display_name="Skip Empty", advanced=True),
        IntInput(
            name="dimensions",
            display_name="Dimensions",
            info="The number of dimensions the resulting output embeddings should have. "
                 "Only supported by certain models.",
            advanced=True,
        ),
    ]

    def build_embeddings(self) -> Embeddings:
        base_url = os.environ.get("AI_GATEWAY_BASE_URL")
        if not base_url:
            msg = "AI_GATEWAY_BASE_URL environment variable not set"
            raise ValueError(msg)

        return OpenAIEmbeddings(
            model=self.model,
            dimensions=self.dimensions or None,
            base_url=base_url,
            embedding_ctx_length=self.embedding_ctx_length,
            check_embedding_ctx_length=False,
            api_key=SecretStr("docspace"),
            allowed_special="all",
            disallowed_special="all",
            chunk_size=self.chunk_size,
            max_retries=self.max_retries,
            timeout=self.request_timeout or None,
            show_progress_bar=self.show_progress_bar,
            model_kwargs=self.model_kwargs,
            skip_empty=self.skip_empty,
            default_headers={
                "origin": self.portal_url,
                "cookie": f"asc_auth_key={self.api_key};"
            },
        )
