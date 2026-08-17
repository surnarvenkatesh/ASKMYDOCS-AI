"""
Embedding provider — a thin, swappable wrapper so the rest of the
retrieval pipeline never imports sentence-transformers or openai
directly. Models are loaded lazily and cached at module scope since
loading a transformer model is expensive (~seconds) and should happen
once per process, not once per request.
"""
from __future__ import annotations

from functools import lru_cache

from app.core.config import settings


class EmbeddingProvider:
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]

    @property
    def dimension(self) -> int:
        raise NotImplementedError


class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL) -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)
        self._dimension = self._model.get_sentence_embedding_dimension()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return vectors.tolist()

    @property
    def dimension(self) -> int:
        return self._dimension


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "text-embedding-3-small") -> None:
        from openai import OpenAI

        self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self._model_name = model_name
        self._dimension = 1536  # text-embedding-3-small

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = self._client.embeddings.create(model=self._model_name, input=texts)
        return [item.embedding for item in response.data]

    @property
    def dimension(self) -> int:
        return self._dimension


class GeminiEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "text-embedding-004") -> None:
        from google import genai

        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self._model_name = model_name
        self._dimension = 768  # text-embedding-004

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        result = self._client.models.embed_content(model=self._model_name, contents=texts)
        return [e.values for e in result.embeddings]

    @property
    def dimension(self) -> int:
        return self._dimension


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    """Process-wide singleton so the model is loaded exactly once."""
    if settings.EMBEDDING_PROVIDER == "openai":
        return OpenAIEmbeddingProvider()
    if settings.EMBEDDING_PROVIDER == "gemini":
        return GeminiEmbeddingProvider()
    return HuggingFaceEmbeddingProvider()
