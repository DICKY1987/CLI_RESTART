from src.observability.metrics import (
    observe_workflow_start,
    observe_workflow_end,
    observe_ai_tokens,
    observe_workflow_error,
)


def test_metrics_observers_do_not_raise():
    observe_workflow_start()
    observe_ai_tokens("model-x", 10)
    observe_workflow_error("TypeError")
    observe_workflow_end(True, 0.01)