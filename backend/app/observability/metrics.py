from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
)

ACTIVE_REQUESTS = Gauge(
    "http_requests_active",
    "Currently active requests",
)

LLM_LATENCY = Histogram(
    "llm_latency_seconds",
    "LLM generation latency",
)

EMBEDDING_LATENCY = Histogram(
    "embedding_latency_seconds",
    "Embedding generation latency",
)

RETRIEVAL_LATENCY = Histogram(
    "retrieval_latency_seconds",
    "Vector retrieval latency",
)

TOOL_LATENCY = Histogram(
    "tool_latency_seconds",
    "Tool execution latency",
)

TOOL_CALL_COUNTER = Counter(
    "tool_calls_total",
    "Total tool calls",
    ["tool"],
)

RETRIEVAL_RESULTS = Histogram(
    "retrieval_results",
    "Number of retrieved chunks",
)

INGESTION_LATENCY = Histogram(
    "document_ingestion_seconds",
    "Document ingestion latency",
)

DOCUMENT_CHUNKS = Histogram(
    "document_chunks",
    "Chunks produced per document",
)

AGENT_ITERATIONS = Histogram(
    "agent_iterations",
    "Agent iterations before completion",
)

LLM_PROMPT_TOKENS = Counter(
    "llm_prompt_tokens_total",
    "Prompt tokens",
)

LLM_COMPLETION_TOKENS = Counter(
    "llm_completion_tokens_total",
    "Completion tokens",
)

LLM_TOTAL_REQUESTS = Counter(
    "llm_requests_total",
    "Total LLM requests",
)

LLM_FAILED_REQUESTS = Counter(
    "llm_failed_requests_total",
    "Failed LLM requests",
)


def metrics_response():
    from fastapi.responses import Response

    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
