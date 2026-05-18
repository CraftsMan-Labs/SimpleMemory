from __future__ import annotations

from typing import Protocol


class EmbeddingProvider(Protocol):
    """Abstract embedding API -- swap OpenAI/Cohere/local models."""

    async def embed_texts(self, texts: list[str]) -> list[list[float]]: ...
    async def embed_text(self, text: str) -> list[float]: ...

    @property
    def vector_size(self) -> int: ...

    @property
    def model_name(self) -> str: ...
