import json
import logging

from google import genai

from backend.app.ai.memory.base import MemoryCandidate, MemoryProvider
from backend.app.core.config import settings
from backend.app.models.memory import MemoryType

logger = logging.getLogger(__name__)


class GeminiMemoryProvider(MemoryProvider):
    def __init__(
        self,
        client: genai.Client | None = None,
        model: str = "gemini-flash-lite-latest",
    ) -> None:
        self.client = client or genai.Client(api_key=settings.gemini_api_key)
        self.model = model

    async def summarize(
        self,
        messages: list[dict[str, str]],
        existing_summary: str | None = None,
    ) -> str:
        conversation = "\n".join(
            f"{message['role']}: {message['content']}" for message in messages
        )

        previous_summary = (
            f"\nExisting summary:\n{existing_summary}\n" if existing_summary else ""
        )

        prompt = f"""
Create a concise factual summary of the conversation.

Preserve:
- important facts
- decisions
- user goals
- unresolved questions
- important technical context

Do not invent information.

{previous_summary}

Conversation:
{conversation}

Return only the summary.
""".strip()

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return response.text.strip()

    async def extract_memories(
        self,
        messages: list[dict[str, str]],
    ) -> list[MemoryCandidate]:
        conversation = "\n".join(
            f"{message['role']}: {message['content']}" for message in messages
        )

        prompt = f"""
    Extract only durable information about the user that would be useful
    in future conversations.

    Possible memory types:
    - FACT
    - PREFERENCE
    - GOAL
    - INSTRUCTION

    Rules:
    - Only extract information explicitly stated by the user.
    - Do not infer sensitive personal information.
    - Do not store temporary conversational details.
    - Do not store information about other people.
    - Use a short, stable key.
    - Keep the value concise.
    - Return an empty JSON array if there is nothing worth remembering.

    Return ONLY valid JSON:

    [
    {{
        "memory_type": "preference",
        "memory_key": "preferred_language",
        "memory_value": "Python"
    }}
    ]

    Conversation:
    {conversation}
    """.strip()

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
            },
        )

        data = json.loads(response.text)

        if not data:
            return []

        memories: list[MemoryCandidate] = []

        for item in data:
            try:
                memory_type = MemoryType(item["memory_type"].lower())

                memories.append(
                    MemoryCandidate(
                        memory_type=memory_type,
                        memory_key=item["memory_key"],
                        memory_value=item["memory_value"],
                    )
                )
            except (KeyError, TypeError, ValueError):
                continue

        return memories
