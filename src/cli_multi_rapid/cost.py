from __future__ import annotations

import json
import os
from pathlib import Path


def check_budget() -> None:
    """Emit a minimal cost budget artifact from env configuration.

    This provides a deterministic, scriptable check for CI.
    """
    budget = {
        "max_tokens": int(os.getenv("SIMPLIFIED_MAX_TOKENS", "8000")),
        "cost_limit_usd": os.getenv("SIMPLIFIED_COST_LIMIT_USD", "1.50"),
        "ai_fallback_only": os.getenv("SIMPLIFIED_AI_FALLBACK_ONLY", "true").lower()
        in {"1", "true", "yes"},
    }

    out_dir = Path("cost")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "budget.json").write_text(json.dumps(budget, indent=2))
    print("cost-check: wrote cost/budget.json")


if __name__ == "__main__":
    check_budget()
