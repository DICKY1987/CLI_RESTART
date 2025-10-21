import os
from typing import Optional


def init_tracing(service_name: str = "cli-multi-rapid", otlp_endpoint: Optional[str] = None) -> None:
    """Initialize OpenTelemetry tracing if dependencies are available.

    Uses OTLP exporter if `otlp_endpoint` or `OTEL_EXPORTER_OTLP_ENDPOINT` is set.
    Falls back to a no-op if OpenTelemetry packages are not installed.
    """
    try:
        from opentelemetry import trace  # type: ignore
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,  # type: ignore
        )
        from opentelemetry.sdk.resources import Resource  # type: ignore
        from opentelemetry.sdk.trace import TracerProvider  # type: ignore
        from opentelemetry.sdk.trace.export import (  # type: ignore
            BatchSpanProcessor,
            ConsoleSpanExporter,
        )
    except Exception:
        # OpenTelemetry not installed; run without tracing
        return None

    endpoint = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    if endpoint:
        exporter = OTLPSpanExporter(endpoint=endpoint)
    else:
        exporter = ConsoleSpanExporter()

    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)
    return None
