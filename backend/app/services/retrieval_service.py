from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.ai.embeddings.base import BaseEmbeddingProvider
from backend.app.ai.prompt_builder import PromptBuilder
from backend.app.ai.vector_store.base import BaseVectorStore


class RetrievalService:
    def __init__(
        self,
        embedding_provider: BaseEmbeddingProvider,
        vector_store: BaseVectorStore,
        default_limit: int = 4,
    ):
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.default_limit = default_limit

    async def build_context(
        self,
        session: AsyncSession,
        user_id: int,
        query: str,
        limit: int | None = None,
    ) -> str | None:
        query_embedding = await self.embedding_provider.embed_query(query)
        chunks = await self.vector_store.similarity_search(
            session=session,
            user_id=user_id,
            query_embedding=query_embedding,
            limit=limit or self.default_limit,
        )
        return PromptBuilder.format_retrieved_context(chunks)
