from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


class CostCalculator:
    """Model-aware token->cost calculator with optional registry."""

    _CACHE: Optional[dict[str, float]] = None

    def __init__(self, registry_path: Path | None = None) -> None:
        self.registry_path = registry_path or (Path("config") / "cost_registry.yaml")

    def per_token(self, model: str) -> float:
        model_key = (model or "").strip().lower() or "unknown"
        registry = self._load_registry_mapping()
        if registry and model_key in registry:
            return registry[model_key]

        # Conservative fallbacks
        costs = {
            "gpt-4": 0.00006,
            "gpt-3.5-turbo": 0.000002,
            "claude-3": 0.00008,
            "claude-instant": 0.00024,
        }
        return costs.get(model_key, 0.00001)

    def _load_registry_mapping(self) -> Optional[dict[str, float]]:
        if CostCalculator._CACHE is not None:
            return CostCalculator._CACHE
        try:
            if yaml is None or not self.registry_path.exists():
                CostCalculator._CACHE = None
                return CostCalculator._CACHE
            with open(self.registry_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            result: dict[str, float] = {}
            vendors = (data or {}).get("vendors", {})
            for _vendor, vdata in (vendors or {}).items():
                models = (vdata or {}).get("models", {})
                for model_name, mdata in (models or {}).items():
                    per_1k = None
                    if isinstance(mdata, dict):
                        inp = mdata.get("input_per_1k")
                        out = mdata.get("output_per_1k")
                        if isinstance(inp, (int, float)) and isinstance(out, (int, float)):
                            per_1k = (float(inp) + float(out)) / 2.0
                        elif isinstance(inp, (int, float)):
                            per_1k = float(inp)
                        elif isinstance(out, (int, float)):
                            per_1k = float(out)
                        elif isinstance(mdata.get("per_1k"), (int, float)):
                            per_1k = float(mdata["per_1k"])
                    if per_1k is not None:
                        result[str(model_name).lower()] = per_1k / 1000.0
            CostCalculator._CACHE = result or None
            return CostCalculator._CACHE
        except Exception:
            CostCalculator._CACHE = None
            return CostCalculator._CACHE

