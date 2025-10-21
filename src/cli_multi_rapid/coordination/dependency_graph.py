from __future__ import annotations


def has_cycle(graph: dict[str, set[str]]) -> bool:
    visited: set[str] = set()
    stack: set[str] = set()

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

