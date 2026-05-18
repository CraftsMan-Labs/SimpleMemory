"""OpenTelemetry tracing configuration."""
from __future__ import annotations

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter


def configure_tracing(service_name: str, otlp_endpoint: str | None = None) -> None:
    """Set up OTLP tracing. If *otlp_endpoint* is falsy, spans stay in-process only."""
    provider = TracerProvider(
        resource=Resource.create({"service.name": service_name}),
    )
    if otlp_endpoint:
        processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
        provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
