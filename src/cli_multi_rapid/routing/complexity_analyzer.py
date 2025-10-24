from __future__ import annotations

import glob
from pathlib import Path
from typing import Any

from .models import ComplexityAnalysis


class ComplexityAnalyzer:
    """Analyze workflow step complexity to inform routing decisions."""

    def analyze_step(self, step: dict[str, Any]) -> ComplexityAnalysis:
        factors: dict[str, float] = {}

        files = step.get("files", [])
        file_scope = step.get("file_scope", [])
        all_files: list[str] = []

        if isinstance(files, list):
            all_files.extend(files)
        elif isinstance(files, str):
            all_files.append(files)

        if isinstance(file_scope, list):
            all_files.extend(file_scope)
        elif isinstance(file_scope, str):
            all_files.append(file_scope)

        file_count = 0
        estimated_size = 0
        for pattern in all_files:
            try:
                if "*" in pattern or "?" in pattern:
                    matched_files = glob.glob(pattern, recursive=True)
                    file_count += len(matched_files)
                    sample_files = matched_files[:5]
                    for file_path in sample_files:
                        try:
                            size = Path(file_path).stat().st_size
                            # rough upscale from sample
                            estimated_size += int(size * (len(matched_files) / max(1, len(sample_files))))
                        except Exception:
                            estimated_size += 1000
                else:
                    file_count += 1
                    try:
                        estimated_size += Path(pattern).stat().st_size
                    except Exception:
                        estimated_size += 1000
            except Exception:
                file_count += 5
                estimated_size += 5000

        if file_count == 0:
            factors["file_count"] = 0.1
        elif file_count <= 3:
            factors["file_count"] = 0.2
        elif file_count <= 10:
            factors["file_count"] = 0.3
        else:
            factors["file_count"] = 0.4

        if estimated_size < 10_000:
            factors["file_size"] = 0.1
        elif estimated_size < 100_000:
            factors["file_size"] = 0.2
        else:
            factors["file_size"] = 0.3

        operation_type = self._infer_operation_type(step)
        operation_complexity = {
            "read": 0.1,
            "format": 0.1,
            "lint": 0.15,
            "test": 0.2,
            "edit": 0.25,
            "refactor": 0.3,
            "generate": 0.3,
            "analyze": 0.25,
            "unknown": 0.2,
        }
        factors["operation_type"] = operation_complexity.get(operation_type, 0.2)

        with_params = step.get("with", {})
        if isinstance(with_params, dict):
            param_count = len(with_params)
            nested_complexity = any(isinstance(v, (dict, list)) for v in with_params.values())
            if param_count == 0:
                factors["configuration"] = 0.05
            elif param_count <= 3 and not nested_complexity:
                factors["configuration"] = 0.1
            elif param_count <= 6 or nested_complexity:
                factors["configuration"] = 0.15
            else:
                factors["configuration"] = 0.2
        else:
            factors["configuration"] = 0.1

        context_deps = step.get("context", {})
        retry_config = step.get("retry", {})
        when_condition = step.get("when")

        context_score = 0.0
        if context_deps:
            context_score += 0.1
        if retry_config:
            context_score += 0.05
        if when_condition:
            context_score += 0.05
        factors["context_deps"] = min(context_score, 0.2)

        score = min(sum(factors.values()), 1.0)

        deterministic_confidence = max(0.0, 1.0 - score)
        if operation_type in ["read", "format", "lint"]:
            deterministic_confidence += 0.2
        if file_count <= 5 and estimated_size < 50_000:
            deterministic_confidence += 0.1
        deterministic_confidence = min(deterministic_confidence, 1.0)

        return ComplexityAnalysis(
            score=score,
            factors=factors,
            file_count=file_count,
            estimated_file_size=estimated_size,
            operation_type=operation_type,
            deterministic_confidence=deterministic_confidence,
        )

    def _infer_operation_type(self, step: dict[str, Any]) -> str:
        actor = step.get("actor", "")
        name = str(step.get("name", "")).lower()
        # actor hints
        if "diagnostic" in actor or "lint" in actor:
            return "lint"
        if "test" in actor or "pytest" in actor:
            return "test"
        if "fix" in actor or "format" in actor:
            return "format"
        if "edit" in actor or "ai_" in actor:
            return "edit"
        if "git" in actor:
            return "read"
        # name hints
        if any(w in name for w in ["read", "get", "fetch", "load"]):
            return "read"
        if any(w in name for w in ["format", "fix", "clean"]):
            return "format"
        if any(w in name for w in ["lint", "check", "validate"]):
            return "lint"
        if any(w in name for w in ["test", "verify"]):
            return "test"
        if any(w in name for w in ["edit", "modify", "change", "update"]):
            return "edit"
        if any(w in name for w in ["refactor", "restructure"]):
            return "refactor"
        if any(w in name for w in ["generate", "create", "build"]):
            return "generate"
        if any(w in name for w in ["analyze", "review", "assess"]):
            return "analyze"
        return "unknown"

