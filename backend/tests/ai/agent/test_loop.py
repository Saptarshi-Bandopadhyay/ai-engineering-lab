from typing import ClassVar

from backend.app.ai.agent import AgentLoop, AgentLoopConfig, AgentStopReason
from backend.app.ai.llm.base import BaseLLMProvider, LLMResponse
from backend.app.ai.llm.tooling import LLMToolCall
from backend.app.ai.tools.base import BaseTool, ToolResult
from backend.app.ai.tools.registry import ToolRegistry


class MockCalculatorTool(BaseTool):
    name = "calculator"
    description = "Calculate a mathematical expression."
    parameters: ClassVar[dict] = {
        "type": "object",
        "properties": {
            "expression": {"type": "string"},
        },
        "required": ["expression"],
    }

    async def execute(self, arguments: dict) -> ToolResult:
        return ToolResult(
            tool_call_id="",
            name=self.name,
            content="4",
        )


class ToolCallingLLM(BaseLLMProvider):
    def __init__(self):
        self.calls = 0

    async def complete(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
        tools=None,
        tool_choice="auto",
    ) -> LLMResponse:
        self.calls += 1

        if self.calls == 1:
            return LLMResponse(
                content="",
                provider_model="mock-model",
                prompt_tokens=10,
                completion_tokens=5,
                latency_ms=10,
                tool_calls=[
                    LLMToolCall(
                        id="call-1",
                        name="calculator",
                        arguments={"expression": "2 + 2"},
                    )
                ],
            )

        return LLMResponse(
            content="The answer is 4.",
            provider_model="mock-model",
            prompt_tokens=20,
            completion_tokens=5,
            latency_ms=10,
        )

    async def stream(
        self, messages, system_prompt=None, tools=None, tool_choice="auto"
    ):
        raise NotImplementedError


async def test_agent_executes_tool_then_returns_final_response():
    llm = ToolCallingLLM()

    registry = ToolRegistry(
        [
            MockCalculatorTool(),
        ]
    )

    agent = AgentLoop(
        llm_provider=llm,
        tool_registry=registry,
    )

    result = await agent.run(
        messages=[
            {
                "role": "user",
                "content": "What is 2 + 2?",
            }
        ]
    )

    assert result.content == "The answer is 4."
    assert result.stop_reason == AgentStopReason.FINAL_RESPONSE
    assert result.iterations == 2

    assert len(result.steps) == 2

    first_step = result.steps[0]

    assert len(first_step.actions) == 1
    assert first_step.actions[0].tool_call is not None
    assert first_step.actions[0].tool_call.name == "calculator"

    assert len(first_step.tool_results) == 1
    assert first_step.tool_results[0].content == "4"


async def test_agent_stops_at_max_iterations():
    class NeverEndingLLM(ToolCallingLLM):
        async def complete(
            self,
            messages,
            system_prompt=None,
            tools=None,
            tool_choice="auto",
        ):
            self.calls += 1

            return LLMResponse(
                content="",
                provider_model="mock-model",
                prompt_tokens=10,
                completion_tokens=5,
                latency_ms=10,
                tool_calls=[
                    LLMToolCall(
                        id=f"call-{self.calls}",
                        name="calculator",
                        arguments={"expression": "2 + 2"},
                    )
                ],
            )

    agent = AgentLoop(
        llm_provider=NeverEndingLLM(),
        tool_registry=ToolRegistry([MockCalculatorTool()]),
        config=AgentLoopConfig(max_iterations=3),
    )

    result = await agent.run(
        messages=[
            {
                "role": "user",
                "content": "Keep calculating.",
            }
        ]
    )

    assert result.stop_reason == AgentStopReason.MAX_ITERATIONS
    assert result.iterations == 3
    assert len(result.steps) == 3

    async def test_agent_stream_executes_tools_before_final_response():
        llm = ToolCallingLLM()

        registry = ToolRegistry(
            [
                MockCalculatorTool(),
            ]
        )

        agent = AgentLoop(
            llm_provider=llm,
            tool_registry=registry,
        )

        results = []

        async for result in agent.run_with_final_stream(
            messages=[
                {
                    "role": "user",
                    "content": "What is 2 + 2?",
                }
            ]
        ):
            results.append(result)

        assert len(results) == 1

        result = results[0]

        assert result["type"] == "final_response"
        assert result["content"] == "The answer is 4."
        assert result["iterations"] == 2
        assert result["provider_model"] == "mock-model"
        assert len(result["steps"]) == 2

        first_step = result["steps"][0]

        assert len(first_step.tool_results) == 1
        assert first_step.tool_results[0].content == "4"
