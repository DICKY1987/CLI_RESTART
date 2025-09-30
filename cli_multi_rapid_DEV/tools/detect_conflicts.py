#!/usr/bin/env python3
"""
Intelligent conflict detection and parallelization analyzer for workflows.
"""
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple, Set


@dataclass
class TaskMeta:
    id: str
    phase: str
    files_read: Set[str] = field(default_factory=set)
    files_write: Set[str] = field(default_factory=set)
    commands: List[str] = field(default_factory=list)


class ParallelizationDetector:
    def __init__(self):
        self.tasks: Dict[str, TaskMeta] = {}
        self.phases: Dict[str, Dict] = {}

    def load_plan(self, plan_path: Path) -> None:
        data = json.loads(plan_path.read_text())
        self.phases = {p["id"]: p for p in data.get("phases", [])}
        for phase in data.get("phases", []):
            for task in phase.get("tasks", []):
                tm = TaskMeta(
                    id=task.get("id", ""),
                    phase=phase.get("id", ""),
                    files_read=set(task.get("reads", [])),
                    files_write=set(task.get("writes", [])),
                    commands=task.get("commands", []),
                )
                self.tasks[tm.id] = tm

    def detect_conflicts(self) -> Tuple[List[Tuple[str, str]], List[List[str]], List[str]]:
        conflicts: List[Tuple[str, str]] = []
        for a_id, a in self.tasks.items():
            for b_id, b in self.tasks.items():
                if a_id >= b_id:
                    continue
                if a.files_write & b.files_write:
                    conflicts.append((a_id, b_id))
                elif (a.files_write & b.files_read) or (b.files_write & a.files_read):
                    conflicts.append((a_id, b_id))

        # Build naive parallel groups per phase: tasks without conflicts together
        parallel_groups: List[List[str]] = []
        for phase_id in self.phases:
            phase_tasks = [t.id for t in self.tasks.values() if t.phase == phase_id]
            group: List[str] = []
            for t in phase_tasks:
                if all((t, g) not in conflicts and (g, t) not in conflicts for g in group):
                    group.append(t)
            if group:
                parallel_groups.append(group)

        must_be_sequential: List[str] = []
        for a, b in conflicts:
            must_be_sequential.append(f"{a} -> {b}")

        return conflicts, parallel_groups, must_be_sequential


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Analyze combined plan for conflicts")
    parser.add_argument("plan", type=Path, help="Path to combined plan JSON")
    parser.add_argument("--output", "-o", type=Path, default=None)
    args = parser.parse_args()

    detector = ParallelizationDetector()
    detector.load_plan(args.plan)
    conflicts, groups, seq = detector.detect_conflicts()

    result = {
        "conflicts": conflicts,
        "safe_parallel_groups": groups,
        "must_be_sequential": seq,
        "summary": {
            "total_phases": len(detector.phases),
            "parallel_groups": len(groups),
            "sequential_constraints": len(seq),
        },
    }

    if args.output:
        args.output.write_text(json.dumps(result, indent=2))
        print(f"Analysis saved to {args.output}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

