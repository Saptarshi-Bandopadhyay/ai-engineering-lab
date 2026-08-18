from backend.app.models.message import Message


class PromptBuilder:
    SYSTEM_PROMPT = "You are a helpful AI assistant. Answer clearly and concisely."

    @staticmethod
    def format_history(messages: list[Message]) -> list[dict[str, str]]:
        """Translates our DB models into the generic format expected by the LLM Provider."""
        return [{"role": msg.role.value, "content": msg.content} for msg in messages]

    @classmethod
    def build_system_prompt(cls, retrieved_context: str | None = None) -> str:
        if not retrieved_context:
            return cls.SYSTEM_PROMPT

        return (
            f"{cls.SYSTEM_PROMPT}\n\n"
            "Use the retrieved document context below when it is relevant. "
            "If the context does not contain the answer, say so and answer from "
            "the conversation only when appropriate.\n\n"
            f"Retrieved context:\n{retrieved_context}"
        )

    @staticmethod
    def format_retrieved_context(chunks: list[object]) -> str | None:
        if not chunks:
            return None

        sections = []
        for chunk in chunks:
            document = getattr(chunk, "document", None)
            filename = getattr(document, "filename", "uploaded document")
            chunk_index = getattr(chunk, "chunk_index", 0)
            content = getattr(chunk, "content", "")
            sections.append(f"[{filename}, chunk {chunk_index + 1}]\n{content}")

        return "\n\n".join(sections)
