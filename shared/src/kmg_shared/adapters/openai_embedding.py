from __future__ import annotations

import httpx

from kmg_shared.resilience import retry_transient


class OpenAIEmbedding:
    """EmbeddingProvider implementation using the OpenAI-compatible embeddings API."""

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        dimensions: int = 1536,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._dimensions = dimensions
        self._client = httpx.AsyncClient(
            base_url="https://api.openai.com/v1",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0,
        )

    @retry_transient
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = await self._client.post(
            "/embeddings",
            json={
                "input": texts,
                "model": self._model,
                "dimensions": self._dimensions,
            },
        )
        response.raise_for_status()
        data = response.json()
        return [item["embedding"] for item in data["data"]]

    @retry_transient
    async def embed_text(self, text: str) -> list[float]:
        results = await self.embed_texts([text])
        return results[0]

    @property
    def vector_size(self) -> int:
        return self._dimensions

    @property
    def model_name(self) -> str:
        return self._model
