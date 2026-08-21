import time

from opentelemetry import trace

from backend.app.ai.agent.base import (
    AgentAction,
    AgentLoopConfig,
    AgentLoopResult,
    AgentStep,
    AgentStopReason,
)
from backend.app.ai.llm.base import BaseLLMProvider, LLMResponse
from backend.app.ai.tools.registry import ToolRegistry
from backend.app.observability.metrics import (
    AGENT_ITERATIONS,
    TOOL_CALL_COUNTER,
    TOOL_LATENCY,
)

tracer = trace.get_tracer(__name__)


class AgentLoop:
    """
    Provider-independent agent execution loop.

    The loop repeatedly:
        1. Calls the LLM.
        2. Inspects the returned tool calls.
        3. Executes requested tools.
        4. Adds tool results to the conversation.
        5. Calls the LLM again.

    The loop terminates when the LLM returns a normal response or
    the configured maximum number of iterations is reached.
    """

    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        tool_registry: ToolRegistry,
        config: AgentLoopConfig | None = None,
    ):
        self.llm_provider = llm_provider
        self.tool_registry = tool_registry
        self.config = config or AgentLoopConfig()

    async def run(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
    ) -> AgentLoopResult:
        """
        Execute the agent loop.

        The supplied messages are copied so the caller's history is not
        mutated by tool-call/tool-result messages generated during execution.
        """

        with tracer.start_as_current_span("agent.run") as span:
            span.set_attribute("agent.max_iterations", self.config.max_iterations)

            working_messages = list(messages)
            steps = []

        for iteration in range(1, self.config.max_iterations + 1):
            with tracer.start_as_current_span("agent.iteration") as iteration_span:
                iteration_span.set_attribute("iteration", iteration)

            with tracer.start_as_current_span("llm.complete"):
                response = await self.llm_provider.complete(
                    working_messages,
                    system_prompt=system_prompt,
                    tools=self.tool_registry.definitions(),
                    tool_choice="auto",
                )

            actions = self._build_actions(response)

            step = AgentStep(
                iteration=iteration,
                llm_response=response,
                actions=actions,
            )

            # No tool calls means the LLM has produced the final response.
            if not response.tool_calls:
                steps.append(step)

                AGENT_ITERATIONS.observe(iteration)

                span.set_attribute("agent.stop_reason", "final_response")

                return AgentLoopResult(
                    content=response.content,
                    steps=steps,
                    stop_reason=AgentStopReason.FINAL_RESPONSE,
                    iterations=iteration,
                    provider_model=response.provider_model,
                    prompt_tokens=response.prompt_tokens,
                    completion_tokens=response.completion_tokens,
                    latency_ms=response.latency_ms,
                )

            # Preserve the assistant's tool-call decision in the history.
            working_messages.append(self._build_assistant_tool_message(response))

            tool_results = []

            for tool_call in response.tool_calls:
                TOOL_CALL_COUNTER.labels(tool_call.name).inc()

                start = time.perf_counter()

                with tracer.start_as_current_span(
                    f"tool.{tool_call.name}"
                ) as tool_span:
                    tool_span.set_attribute("tool.name", tool_call.name)

                    result = await self.tool_registry.execute(
                        tool_call_id=tool_call.id,
                        name=tool_call.name,
                        arguments=tool_call.arguments,
                    )

                TOOL_LATENCY.labels(tool_call.name).observe(time.perf_counter() - start)

                tool_results.append(result)

                working_messages.append(self._build_tool_result_message(result))

            step.tool_results = tool_results
            steps.append(step)

        AGENT_ITERATIONS.observe(self.config.max_iterations)
        span.set_attribute("agent.stop_reason", "max_iterations")
        # The LLM kept requesting tools without producing a final answer.
        return AgentLoopResult(
            content="",
            steps=steps,
            stop_reason=AgentStopReason.MAX_ITERATIONS,
            iterations=self.config.max_iterations,
            provider_model=response.provider_model,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            latency_ms=response.latency_ms,
        )

    async def run_with_final_stream(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
    ):
        """
        Execute tool-calling iterations and stream the final response.

        Tool-calling iterations use ``complete()`` because we need the full
        LLM response to inspect and execute tool calls.

        Once the LLM produces a response without tool calls, that response
        is the final answer and is returned as a stream.

        This keeps tool execution provider-independent while preserving the
        existing streaming interface used by the API.
        """

        with tracer.start_as_current_span("agent.run") as span:
            span.set_attribute("agent.max_iterations", self.config.max_iterations)

            working_messages = list(messages)
            steps = []

        for iteration in range(1, self.config.max_iterations + 1):
            with tracer.start_as_current_span("agent.iteration") as iteration_span:
                iteration_span.set_attribute("iteration", iteration)

            response = await self.llm_provider.complete(
                working_messages,
                system_prompt=system_prompt,
                tools=self.tool_registry.definitions(),
                tool_choice="auto",
            )

            actions = self._build_actions(response)

            step = AgentStep(
                iteration=iteration,
                llm_response=response,
                actions=actions,
            )

            # The LLM has produced the final answer.
            if not response.tool_calls:
                steps.append(step)

                yield {
                    "type": "final_response",
                    "content": response.content,
                    "provider_model": response.provider_model,
                    "prompt_tokens": response.prompt_tokens,
                    "completion_tokens": response.completion_tokens,
                    "latency_ms": response.latency_ms,
                    "iterations": iteration,
                    "steps": steps,
                }
                return

            # Preserve the assistant's tool-call decision.
            working_messages.append(self._build_assistant_tool_message(response))

            tool_results = []

            for tool_call in response.tool_calls:
                result = await self.tool_registry.execute(
                    tool_call_id=tool_call.id,
                    name=tool_call.name,
                    arguments=tool_call.arguments,
                )

                tool_results.append(result)

                working_messages.append(self._build_tool_result_message(result))

            step.tool_results = tool_results
            steps.append(step)

        yield {
            "type": "max_iterations",
            "content": "",
            "provider_model": response.provider_model,
            "prompt_tokens": response.prompt_tokens,
            "completion_tokens": response.completion_tokens,
            "latency_ms": response.latency_ms,
            "iterations": self.config.max_iterations,
            "steps": steps,
        }

    @staticmethod
    def _build_actions(response: LLMResponse) -> list[AgentAction]:
        if not response.tool_calls:
            return [
                AgentAction.final_response(response.content),
            ]

        return [
            AgentAction.tool_call_action(tool_call) for tool_call in response.tool_calls
        ]

    @staticmethod
    def _build_assistant_tool_message(
        response: LLMResponse,
    ) -> dict:
        """
        Convert an LLM response containing tool calls into the provider-neutral
        conversation representation.

        provider_data is preserved so providers that require opaque response
        metadata, such as Gemini thought signatures, can reconstruct their
        native conversation history correctly.
        """

        return {
            "role": "assistant",
            "content": response.content,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "name": tool_call.name,
                    "arguments": tool_call.arguments,
                    "provider_metadata": tool_call.provider_metadata,
                }
                for tool_call in response.tool_calls or []
            ],
            "provider_data": response.provider_data,
        }

    @staticmethod
    def _build_tool_result_message(tool_result) -> dict:
        """Convert a ToolResult into a provider-neutral tool message."""

        return {
            "role": "tool",
            "tool_call_id": tool_result.tool_call_id,
            "name": tool_result.name,
            "content": tool_result.content,
            "is_error": tool_result.is_error,
        }
