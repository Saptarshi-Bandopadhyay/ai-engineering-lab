import asyncio
import json
import logging
import uuid
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.ai.agent import AgentLoop
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
        retrieval_service: RetrievalService,
        prompt_builder: PromptBuilder,
        agent_loop: AgentLoop,
    ):
        self.conv_service = conv_service
        self.msg_repo = msg_repo
        self.llm_provider = llm_provider
        self.retrieval_service = retrieval_service
        self.prompt_builder = prompt_builder
        self.agent_loop = agent_loop

    async def process_user_message(
        self, session: AsyncSession, conversation_id: int, user_id: int, content: str
    ) -> list:
        # 1. Authorization
        await self.conv_service.get_own_conversation(session, conversation_id, user_id)

        # 2. Persist User Message FIRST (Transaction 1)
        user_msg = self.msg_repo.add(conversation_id, MessageRole.USER, content)
        session.add(user_msg)
        await session.commit()
        await session.refresh(user_msg)

        # 3. Retrieve conversation history and document context
        history = await self.msg_repo.get_history_by_conversation(
            session, conversation_id
        )
        messages = self._build_agent_messages(history)

        retrieved_context = await self._retrieve_context(session, user_id, content)
        system_prompt = PromptBuilder.build_system_prompt(retrieved_context)

        # 4. Run the provider-independent agent loop
        agent_result = await self.agent_loop.run(
            messages=messages,
            system_prompt=system_prompt,
        )

        # 5. Persist the final assistant response
        ai_msg = self.msg_repo.add(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=agent_result.content,
            provider_model=agent_result.provider_model,
            prompt_tokens=agent_result.prompt_tokens,
            completion_tokens=agent_result.completion_tokens,
            latency_ms=agent_result.latency_ms,
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

        messages = [
            {
                "role": message.role.value.lower(),
                "content": message.content,
            }
            for message in history
        ]

        retrieved_context = await self._retrieve_context(session, user_id, content)
        system_prompt = PromptBuilder.build_system_prompt(retrieved_context)

        accumulated_content = ""
        status = MessageStatus.COMPLETED

        # 5. Run the agent loop.
        #
        # Tool-calling iterations are executed internally. Once the agent
        # reaches its final response, we stream that response through the
        # existing SSE interface.
        try:
            async for result in self.agent_loop.run_with_final_stream(
                messages=messages,
                system_prompt=system_prompt,
            ):
                if result["type"] == "final_response":
                    accumulated_content = result["content"]

                    # Stream the final response using the existing SSE
                    # contract. The agent has already completed any required
                    # tool calls before reaching this point.
                    if accumulated_content:
                        yield LLMStreamChunk(
                            event_type=StreamEventType.TOKEN,
                            content=accumulated_content,
                        )

                    metadata = {
                        "provider_model": result["provider_model"],
                        "latency_ms": result["latency_ms"],
                        "prompt_tokens": result["prompt_tokens"],
                        "completion_tokens": result["completion_tokens"],
                    }

                    ai_msg = self.msg_repo.add(
                        conversation_id=conversation_id,
                        role=MessageRole.ASSISTANT,
                        content=accumulated_content,
                        status=status,
                        provider_model=metadata["provider_model"],
                        prompt_tokens=metadata["prompt_tokens"],
                        completion_tokens=metadata["completion_tokens"],
                        latency_ms=metadata["latency_ms"],
                    )

                    session.add(ai_msg)

                    try:
                        await session.commit()

                        logger.info(
                            f"[{request_id}] Assistant message saved. Status: {status}"
                        )

                        yield LLMStreamChunk(
                            event_type=StreamEventType.COMPLETED,
                            content=json.dumps({"id": ai_msg.id}),
                        )

                    except Exception as db_e:
                        await session.rollback()

                        logger.error(
                            f"[{request_id}] Failed to persist AI message: {db_e!s}"
                        )

                elif result["type"] == "max_iterations":
                    status = MessageStatus.FAILED

                    logger.warning(f"[{request_id}] Agent reached maximum iterations.")

                    yield LLMStreamChunk(
                        event_type=StreamEventType.ERROR,
                        content="Agent reached the maximum number of iterations.",
                    )

        except asyncio.CancelledError:
            logger.warning(f"[{request_id}] Client disconnected. Halting generation.")
            raise

        except Exception as e:
            logger.error(f"[{request_id}] Agent execution failed: {e!s}")

            status = MessageStatus.FAILED

            yield LLMStreamChunk(
                event_type=StreamEventType.ERROR,
                content="Generation failed.",
            )

    @staticmethod
    def _build_agent_messages(history) -> list[dict]:
        return [
            {
                "role": message.role.value.lower(),
                "content": message.content,
            }
            for message in history
        ]

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
