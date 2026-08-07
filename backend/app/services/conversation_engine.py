from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.llm.base import BaseLLMProvider
from backend.app.llm.prompt_formatter import PromptFormatter
from backend.app.models.message import MessageRole
from backend.app.repositories.message_repository import MessageRepository
from backend.app.services.conversation_service import ConversationService


class ConversationEngine:
    def __init__(
        self,
        conv_service: ConversationService,
        msg_repo: MessageRepository,
        llm_provider: BaseLLMProvider,
    ):
        self.conv_service = conv_service
        self.msg_repo = msg_repo
        self.llm_provider = llm_provider

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
        formatted_prompt = PromptFormatter.format_history(history)

        # 4. Call LLM (If this fails, an exception is raised, but the user_msg is already safely committed!)
        llm_response = await self.llm_provider.complete(formatted_prompt)

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
