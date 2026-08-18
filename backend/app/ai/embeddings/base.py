from abc import ABC, abstractmethod


class BaseEmbeddingProvider(ABC):
    @abstractmethod
    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embeds document chunks for vector storage."""

    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        """Embeds a user query for retrieval."""
