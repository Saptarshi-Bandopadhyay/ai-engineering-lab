from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_tracing():
    provider = TracerProvider(
        resource=Resource.create(
            {
                "service.name": "ai-engineering-lab",
                "service.version": "0.1.0",
            }
        )
    )

    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))

    trace.set_tracer_provider(provider)

    return trace.get_tracer(__name__)
