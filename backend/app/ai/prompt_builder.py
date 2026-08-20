from backend.app.models.message import Message


class PromptBuilder:
    SYSTEM_PROMPT = "You are a helpful AI assistant. Answer clearly and concisely."

    @staticmethod
    def format_history(messages: list[Message]) -> list[dict[str, str]]:
        """Translate DB models into the generic format expected by the LLM provider."""
        return [
            {
                "role": msg.role.value,
                "content": msg.content,
            }
            for msg in messages
        ]

    @classmethod
    def build_system_prompt(
        cls,
        retrieved_context: str | None = None,
        conversation_summary: str | None = None,
        user_memories: list[object] | None = None,
    ) -> str:
        sections = [cls.SYSTEM_PROMPT]

        if conversation_summary:
            sections.append(f"Conversation summary:\n{conversation_summary}")

        if user_memories:
            memory_lines = []

            for memory in user_memories:
                memory_key = getattr(memory, "memory_key", "")
                memory_value = getattr(memory, "memory_value", "")

                if memory_key and memory_value:
                    memory_lines.append(f"- {memory_key}: {memory_value}")

            if memory_lines:
                sections.append(
                    "Relevant user information:\n" + "\n".join(memory_lines)
                )

        if retrieved_context:
            sections.append(
                "Use the retrieved document context below when it is relevant. "
                "If the context does not contain the answer, say so and answer "
                "from the conversation only when appropriate.\n\n"
                f"Retrieved context:\n{retrieved_context}"
            )

        return "\n\n".join(sections)

    @staticmethod
    def format_retrieved_context(chunks: list[object]) -> str | None:
        if not chunks:
            return None

        sections = []

        for chunk in chunks:
            document = getattr(chunk, "document", None)
            filename = getattr(
                document,
                "filename",
                "uploaded document",
            )
            chunk_index = getattr(chunk, "chunk_index", 0)
            content = getattr(chunk, "content", "")

            sections.append(f"[{filename}, chunk {chunk_index + 1}]\n{content}")

        return "\n\n".join(sections)
