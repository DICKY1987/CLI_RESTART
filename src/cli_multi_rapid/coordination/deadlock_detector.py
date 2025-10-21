from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from .dependency_graph import has_cycle


@dataclass
class DeadlockReport:
    """Report of deadlock detection analysis."""
    cycle_detected: bool
    timed_out: set[str] = field(default_factory=set)
    cycle_nodes: list[str] = field(default_factory=list)
    wait_chain: dict[str, str] = field(default_factory=dict)  # node -> waiting_for
    detection_timestamp: float = field(default_factory=time.time)
    remediation_suggestions: list[str] = field(default_factory=list)


def detect_deadlock(
    graph: dict[str, set[str]],
    start_times: dict[str, float],
    timeout_seconds: float
) -> DeadlockReport:
    """
    Detect deadlocks in a dependency graph.

    Args:
        graph: Dependency graph where keys depend on values
        start_times: Start times for each node
        timeout_seconds: Timeout threshold in seconds

    Returns:
        DeadlockReport with detection results and recommendations
    """
    cycle = has_cycle(graph)
    now = time.time()
    timed_out = {k for k, t in start_times.items() if (now - t) > timeout_seconds}

    report = DeadlockReport(
        cycle_detected=cycle,
        timed_out=timed_out,
        detection_timestamp=now
    )

    # If cycle detected, find the cycle nodes
    if cycle:
        report.cycle_nodes = find_cycle_nodes(graph)
        report.wait_chain = build_wait_chain(graph)
        report.remediation_suggestions = generate_remediation_suggestions(
            report.cycle_nodes,
            timed_out
        )

    # If timeouts but no cycle, suggest timeout increase
    if timed_out and not cycle:
        report.remediation_suggestions.append(
            f"Consider increasing timeout from {timeout_seconds}s for: {', '.join(timed_out)}"
        )

    return report


def find_cycle_nodes(graph: dict[str, set[str]]) -> list[str]:
    """
    Find and return the nodes that are part of a cycle.

    Args:
        graph: Dependency graph

    Returns:
        List of nodes in the cycle
    """
    visited: set[str] = set()
    stack: list[str] = []
    in_stack: set[str] = set()

    def dfs(node: str) -> Optional[list[str]]:
        if node in in_stack:
            # Found a cycle, return the cycle path
            cycle_start = stack.index(node)
            return stack[cycle_start:] + [node]

        if node in visited:
            return None

        visited.add(node)
        stack.append(node)
        in_stack.add(node)

        for neighbor in graph.get(node, set()):
            cycle_path = dfs(neighbor)
            if cycle_path:
                return cycle_path

        stack.pop()
        in_stack.remove(node)
        return None

    for node in list(graph.keys()):
        if node not in visited:
            cycle_path = dfs(node)
            if cycle_path:
                return cycle_path

    return []


def build_wait_chain(graph: dict[str, set[str]]) -> dict[str, str]:
    """
    Build a wait chain showing what each node is waiting for.

    Args:
        graph: Dependency graph

    Returns:
        Dictionary mapping node to what it's waiting for
    """
    wait_chain = {}

    for node, dependencies in graph.items():
        if dependencies:
            # For simplicity, show the first dependency
            # In a real scenario, you might want to show all
            wait_chain[node] = next(iter(dependencies))

    return wait_chain


def generate_remediation_suggestions(
    cycle_nodes: list[str],
    timed_out: set[str]
) -> list[str]:
    """
    Generate suggestions for resolving deadlocks.

    Args:
        cycle_nodes: Nodes involved in the cycle
        timed_out: Nodes that have timed out

    Returns:
        List of remediation suggestions
    """
    suggestions = []

    if cycle_nodes:
        suggestions.append(
            f"Cycle detected involving: {' → '.join(cycle_nodes)}"
        )
        suggestions.append(
            "Break the cycle by reordering operations or removing circular dependencies"
        )
        suggestions.append(
            f"Consider canceling one of: {', '.join(cycle_nodes[:2])}"
        )

    if timed_out:
        suggestions.append(
            f"The following operations have timed out: {', '.join(timed_out)}"
        )
        suggestions.append(
            "Consider canceling timed-out operations to free resources"
        )

    if cycle_nodes and timed_out:
        intersection = set(cycle_nodes) & timed_out
        if intersection:
            suggestions.append(
                f"Priority: Cancel these nodes that are both in cycle and timed out: {', '.join(intersection)}"
            )

    return suggestions


def detect_potential_deadlock(
    active_locks: dict[str, set[str]],
    pending_locks: dict[str, set[str]],
    timeout_seconds: float = 60.0
) -> DeadlockReport:
    """
    Detect potential deadlocks based on active and pending locks.

    Args:
        active_locks: Currently held locks (workflow_id -> set of resources)
        pending_locks: Locks waiting to be acquired (workflow_id -> set of resources)
        timeout_seconds: Timeout threshold

    Returns:
        DeadlockReport with detection results
    """
    # Build wait-for graph: workflow A waits for workflow B if B holds a resource A needs
    wait_for_graph: dict[str, set[str]] = {}

    for workflow_id, needed_resources in pending_locks.items():
        wait_for_graph[workflow_id] = set()

        for other_workflow_id, held_resources in active_locks.items():
            if workflow_id != other_workflow_id:
                # Check if there's overlap
                if needed_resources & held_resources:
                    wait_for_graph[workflow_id].add(other_workflow_id)

    # Use existing deadlock detection
    start_times = {wid: time.time() for wid in wait_for_graph.keys()}

    return detect_deadlock(wait_for_graph, start_times, timeout_seconds)

