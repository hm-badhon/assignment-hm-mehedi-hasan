from typing import Any, Callable, List, Optional

from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from google import genai
from google.genai import types
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

from src.utils.config import get_settings
from src.utils.logger import get_logger

# mypy: disable-error-code="return-value,index"
settings = get_settings()
logger = get_logger(__name__)

RESPONSE_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "gemini-embedding-001"


def _create_gemini_model(
    model_name: str,
    temperature: float = 0.0,
    streaming: bool = False,
) -> ChatGoogleGenerativeAI:
    """Creates a ChatGoogleGenerativeAI model instance."""
    logger.info(f"Creating Gemini model: {model_name}")
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=temperature,
        disable_streaming=not streaming,
        thinking_budget=0,
    )


def get_response_llm(
    temperature: Optional[float] = None,
) -> BaseChatModel:
    """
    Returns an LLM for generating responses

    Base: Gemini gemini-2.5-flash.
    """
    temp = temperature if temperature is not None else settings.MODEL_TEMPERATURE

    base_llm = _create_gemini_model(
        model_name=RESPONSE_MODEL,
        temperature=temp,
        streaming=True,
    )
    return base_llm


def get_gemini_model(
    model_name: str = RESPONSE_MODEL,
    temperature: float = 0.0,
    streaming: bool = False,
) -> ChatGoogleGenerativeAI:
    """Convenience wrapper to create a Gemini chat model.

    This keeps backward-compatibility with earlier code that imported
    ``get_gemini_model`` directly from this module.
    """
    return _create_gemini_model(
        model_name, temperature=temperature, streaming=streaming
    )


class GeminiEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        EMBEDDING_MODEL_ID = EMBEDDING_MODEL
        title = "Custom query"
        response = client.models.embed_content(
            model=EMBEDDING_MODEL_ID,
            contents=input,
            config=types.EmbedContentConfig(
                task_type="retrieval_document", title=title
            ),
        )
        return [embedding.values for embedding in response.embeddings]
