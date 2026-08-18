from google import genai
from google.genai import types

from backend.app.ai.embeddings.base import BaseEmbeddingProvider
from backend.app.core.config import settings
from backend.app.core.exceptions import ThirdPartyServiceError


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.default_embedding_model
        self.dimensions = settings.embedding_dimensions

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return await self._embed(texts, task_type="RETRIEVAL_DOCUMENT")

    async def embed_query(self, text: str) -> list[float]:
        embeddings = await self._embed([text], task_type="RETRIEVAL_QUERY")
        return embeddings[0]

    async def _embed(self, texts: list[str], task_type: str) -> list[list[float]]:
        if not texts:
            return []

        try:
            response = await self.client.aio.models.embed_content(
                model=self.model,
                contents=texts,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=self.dimensions,
                ),
            )
            return [list(embedding.values) for embedding in response.embeddings]
        except Exception as e:
            raise ThirdPartyServiceError(f"Gemini embedding failed: {e!s}")
