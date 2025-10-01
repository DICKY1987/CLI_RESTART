from __future__ import annotations

from typing import Dict, Set


def has_cycle(graph: Dict[str, Set[str]]) -> bool:
    visited: Set[str] = set()
    stack: Set[str] = set()

    def dfs(node: str) -> bool:
        if node in stack:
            return True
        if node in visited:
            return False
        visited.add(node)
        stack.add(node)
        for nei in graph.get(node, set()):
            if dfs(nei):
                return True
        stack.remove(node)
        return False

    return any(dfs(n) for n in list(graph.keys()))

