from backend.app.models.message import Message


class PromptBuilder:
    @staticmethod
    def format_history(messages: list[Message]) -> list[dict[str, str]]:
        """Translates our DB models into the generic format expected by the LLM Provider."""
        return [{"role": msg.role.value, "content": msg.content} for msg in messages]
