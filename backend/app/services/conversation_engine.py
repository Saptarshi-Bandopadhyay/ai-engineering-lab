import asyncio
import json
import logging
import uuid
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.ai.llm.base import BaseLLMProvider, LLMStreamChunk, StreamEventType
from backend.app.ai.prompt_builder import PromptBuilder
from backend.app.models.message import MessageRole, MessageStatus
from backend.app.repositories.message_repository import MessageRepository
from backend.app.services.conversation_service import ConversationService
from backend.app.services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)


class ConversationEngine:
    def __init__(
        self,
        conv_service: ConversationService,
        msg_repo: MessageRepository,
        llm_provider: BaseLLMProvider,
        retrieval_service: RetrievalService | None = None,
    ):
        self.conv_service = conv_service
        self.msg_repo = msg_repo
        self.llm_provider = llm_provider
        self.retrieval_service = retrieval_service

    async def process_user_message(
        self, session: AsyncSession, conversation_id: int, user_id: int, content: str
    ) -> list:
        # 1. Authorization: Will raise NotFoundError if it's not their conversation
        await self.conv_service.get_own_conversation(session, conversation_id, user_id)

        # 2. Persist User Message FIRST (Transaction 1)
        user_msg = self.msg_repo.add(conversation_id, MessageRole.USER, content)
        session.add(user_msg)
        await session.commit()
        await session.refresh(user_msg)

        # 3. Retrieve formatted history
        history = await self.msg_repo.get_history_by_conversation(
            session, conversation_id
        )
        formatted_prompt = PromptBuilder.format_history(history)
        retrieved_context = await self._retrieve_context(session, user_id, content)
        system_prompt = PromptBuilder.build_system_prompt(retrieved_context)

        # 4. Call LLM (If this fails, an exception is raised, but the user_msg is already safely committed!)
        llm_response = await self.llm_provider.complete(
            formatted_prompt, system_prompt=system_prompt
        )

        # 5. Persist Assistant Response (Transaction 2)
        ai_msg = self.msg_repo.add(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=llm_response.content,
            provider_model=llm_response.provider_model,
            prompt_tokens=llm_response.prompt_tokens,
            completion_tokens=llm_response.completion_tokens,
            latency_ms=llm_response.latency_ms,
        )
        session.add(ai_msg)
        await session.commit()
        await session.refresh(ai_msg)

        return [user_msg, ai_msg]

    async def stream_message(
        self, session: AsyncSession, conversation_id: int, user_id: int, content: str
    ) -> AsyncGenerator[LLMStreamChunk]:
        # 1. Tracing: Assign a unique request ID for observability
        request_id = str(uuid.uuid4())
        logger.info(
            f"[{request_id}] Starting stream for conversation {conversation_id}"
        )

        # 2. Authorization
        await self.conv_service.get_own_conversation(session, conversation_id, user_id)

        # 3. Persist User Message (Transaction 1)
        user_msg = self.msg_repo.add(
            conversation_id, MessageRole.USER, content, status=MessageStatus.COMPLETED
        )
        session.add(user_msg)
        await session.commit()
        await session.refresh(user_msg)

        # Yield the user message creation event
        yield LLMStreamChunk(
            event_type=StreamEventType.USER_MESSAGE,
            content=json.dumps({"id": user_msg.id, "content": user_msg.content}),
        )

        # 4. Prepare Workflow State
        history = await self.msg_repo.get_history_by_conversation(
            session, conversation_id
        )
        formatted_prompt = PromptBuilder.format_history(history)
        retrieved_context = await self._retrieve_context(session, user_id, content)
        system_prompt = PromptBuilder.build_system_prompt(retrieved_context)

        accumulated_content = ""
        status = MessageStatus.COMPLETED
        metadata = {}

        # 5. The Three-Way Async Pipe
        try:
            async for chunk in self.llm_provider.stream(
                formatted_prompt, system_prompt=system_prompt
            ):
                if chunk.event_type == StreamEventType.TOKEN:
                    accumulated_content += chunk.content
                    yield chunk

                elif chunk.event_type == StreamEventType.COMPLETED:
                    metadata = {
                        "provider_model": chunk.provider_model,
                        "latency_ms": chunk.latency_ms,
                        "prompt_tokens": chunk.prompt_tokens,
                        "completion_tokens": chunk.completion_tokens,
                    }

        except asyncio.CancelledError:
            # Client disconnected mid-stream
            logger.warning(f"[{request_id}] Client disconnected. Halting generation.")
            status = MessageStatus.PARTIAL
            raise  # Bubble up to FastAPI so it closes the socket

        except Exception as e:
            # LLM Provider failed mid-stream
            logger.error(f"[{request_id}] LLM Generation failed: {e!s}")
            status = MessageStatus.FAILED
            yield LLMStreamChunk(
                event_type=StreamEventType.ERROR,
                content="Generation failed mid-stream.",
            )

        finally:
            # 6. Final Persistence (Guaranteed execution)
            if accumulated_content:
                ai_msg = self.msg_repo.add(
                    conversation_id=conversation_id,
                    role=MessageRole.ASSISTANT,
                    content=accumulated_content,
                    status=status,
                    provider_model=metadata.get("provider_model"),
                    prompt_tokens=metadata.get("prompt_tokens"),
                    completion_tokens=metadata.get("completion_tokens"),
                    latency_ms=metadata.get("latency_ms"),
                )
                session.add(ai_msg)

                # We only yield the final COMPLETED event *after* DB commit succeeds.
                try:
                    await session.commit()
                    logger.info(
                        f"[{request_id}] Assistant message saved. Status: {status}"
                    )

                    if status == MessageStatus.COMPLETED:
                        yield LLMStreamChunk(
                            event_type=StreamEventType.COMPLETED,
                            content=json.dumps({"id": ai_msg.id}),
                        )
                except Exception as db_e:
                    logger.error(
                        f"[{request_id}] Failed to persist AI message: {db_e!s}"
                    )
                    # We do not yield the completed event if DB fails.

    async def _retrieve_context(
        self, session: AsyncSession, user_id: int, query: str
    ) -> str | None:
        if self.retrieval_service is None:
            return None

        try:
            return await self.retrieval_service.build_context(session, user_id, query)
        except Exception as e:
            logger.warning("Document retrieval skipped: %s", e)
            return None
