from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

# Business/workflow metrics
WORKFLOW_EXECUTIONS = Counter(
    "workflow_executions_total", "Total workflows executed", ["status"]
)
WORKFLOW_DURATION = Histogram(
    "workflow_duration_seconds", "Workflow execution duration (s)"
)
WORKFLOWS_IN_PROGRESS = Gauge(
    "workflows_in_progress", "Number of workflows currently running"
)
AI_TOKENS_USED = Counter(
    "ai_tokens_used_total", "Total AI tokens used", ["model"]
)
WORKFLOW_ERRORS = Counter(
    "workflow_errors_total", "Total workflow errors", ["type"]
)

# Generic HTTP metrics (opt-in to use)
REQUEST_COUNT = Counter(
    "app_requests_total", "Total HTTP requests", ["route", "method", "code"]
)
REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds", "Request latency (s)", ["route"]
)


def observe_workflow_start() -> None:
    WORKFLOWS_IN_PROGRESS.inc()


def observe_workflow_end(success: bool, duration_s: float) -> None:
    status = "success" if success else "failed"
    WORKFLOW_EXECUTIONS.labels(status=status).inc()
    WORKFLOW_DURATION.observe(max(0.0, float(duration_s)))
    WORKFLOWS_IN_PROGRESS.dec()


def observe_ai_tokens(model: str, tokens: int) -> None:
    AI_TOKENS_USED.labels(model=model or "unknown").inc(max(0, int(tokens)))


def observe_workflow_error(err_type: str) -> None:
    WORKFLOW_ERRORS.labels(type=err_type or "unknown").inc()


def prometheus_wsgi_app(environ, start_response):
    data = generate_latest()
    start_response("200 OK", [("Content-Type", CONTENT_TYPE_LATEST)])
    return [data]