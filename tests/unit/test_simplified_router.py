from src.cli_multi_rapid.routing.simplified_router import SimplifiedRouter


def test_routing_prefers_primary_for_simple_ops():
    router = SimplifiedRouter()
    op = {"type": "edit", "complexity": 1, "file_count": 1, "file_size_kb": 10}
    tool = router.route_operation(op)
    assert isinstance(tool, str) and tool


def test_routing_uses_fallback_for_heavy_ops():
    router = SimplifiedRouter()
    # High complexity and size should push to fallback in many roles
    op = {"type": "edit", "complexity": 10, "file_count": 200, "file_size_kb": 5000}
    tool = router.route_operation(op)
    assert isinstance(tool, str) and tool


def test_cost_estimation_increases_with_complexity():
    router = SimplifiedRouter()
    op_low = {"type": "edit", "complexity": 1, "file_count": 1, "file_size_kb": 10}
    op_high = {"type": "edit", "complexity": 5, "file_count": 1, "file_size_kb": 10}
    tool = router.route_operation(op_low)
    cost_low = router.estimate_operation_cost(op_low, tool)
    cost_high = router.estimate_operation_cost(op_high, tool)
    assert cost_high > cost_low
