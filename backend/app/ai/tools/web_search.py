from typing import Any, ClassVar

import httpx

from backend.app.ai.tools.base import BaseTool, ToolResult


class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the web for information relevant to a user query."

    parameters: ClassVar[dict] = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query.",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return.",
                "minimum": 1,
                "maximum": 10,
            },
        },
        "required": ["query"],
    }

    async def execute(self, arguments: dict[str, Any]) -> ToolResult:
        query = arguments.get("query")
        max_results = min(max(int(arguments.get("max_results", 5)), 1), 10)

        if not isinstance(query, str) or not query.strip():
            return ToolResult(
                tool_call_id="",
                name=self.name,
                content="Search query must be a non-empty string.",
                is_error=True,
            )

        try:
            async with httpx.AsyncClient(
                timeout=10.0,
                headers={"User-Agent": "AI-Workspace/0.1"},
            ) as client:
                response = await client.get(
                    "https://html.duckduckgo.com/html/",
                    params={"q": query},
                )
                response.raise_for_status()

            # Search-engine parsing will be implemented behind this tool boundary.
            # Keeping the external API isolated here means the agent architecture
            # does not depend on a particular search provider.

            return ToolResult(
                tool_call_id="",
                name=self.name,
                content=response.text[: max_results * 2000],
            )

        except httpx.HTTPError as exc:
            return ToolResult(
                tool_call_id="",
                name=self.name,
                content=f"Web search failed: {exc}",
                is_error=True,
            )
