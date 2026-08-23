"""
LLM provider abstraction — streaming chat completion over OpenAI's API
or a local Ollama server, behind one interface so the chat service
never branches on provider.
"""
from __future__ import annotations

from collections.abc import AsyncIterator

from app.core.config import settings


class LLMProvider:
    async def stream(self, system_prompt: str, user_prompt: str) -> AsyncIterator[str]:
        """Yield response text incrementally (token/chunk at a time)."""
        raise NotImplementedError
        yield  # pragma: no cover - makes this an async generator for the ABC


class OpenAILLMProvider(LLMProvider):
    def __init__(self, model: str = settings.OPENAI_MODEL) -> None:
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = model

    async def stream(self, system_prompt: str, user_prompt: str) -> AsyncIterator[str]:
        stream = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=True,
            temperature=0.2,
        )
        async for event in stream:
            delta = event.choices[0].delta.content
            if delta:
                yield delta


class OllamaLLMProvider(LLMProvider):
    def __init__(self, model: str = settings.OLLAMA_MODEL, base_url: str = settings.OLLAMA_BASE_URL) -> None:
        self._model = model
        self._base_url = base_url.rstrip("/")

    async def stream(self, system_prompt: str, user_prompt: str) -> AsyncIterator[str]:
        import httpx

        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=300) as client:
            async with client.stream("POST", f"{self._base_url}/api/chat", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    import orjson

                    event = orjson.loads(line)
                    content = event.get("message", {}).get("content", "")
                    if content:
                        yield content


class GroqLLMProvider(LLMProvider):
    def __init__(self, model: str = settings.GROQ_MODEL) -> None:
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(api_key=settings.GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
        self._model = model

    async def stream(self, system_prompt: str, user_prompt: str) -> AsyncIterator[str]:
        stream = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=True,
            temperature=0.2,
        )
        async for event in stream:
            delta = event.choices[0].delta.content
            if delta:
                yield delta


def get_llm_provider() -> LLMProvider:
    if settings.LLM_PROVIDER == "openai":
        return OpenAILLMProvider()
    if settings.LLM_PROVIDER == "groq":
        return GroqLLMProvider()
    return OllamaLLMProvider()
