from __future__ import annotations

import json
import os
from pathlib import Path


def simplified_run() -> None:
    """Lightweight entry to simulate simplified workflow dry-run.

    Reads environment and prints a small execution config summary so
    CI can confirm parameters without invoking the full orchestrator.
    """
    config = {
        "framework_version": os.getenv("FRAMEWORK_VERSION", "simplified-25ops"),
        "lane": os.getenv("LANE", "lane/quality/quick-fix"),
        "inputs": {
            "files": ["src/**/*.py", "tests/**/*.py"],
        },
        "policy": {
            "max_tokens": int(os.getenv("SIMPLIFIED_MAX_TOKENS", "8000")),
            "cost_limit_usd": os.getenv("SIMPLIFIED_COST_LIMIT_USD", "1.50"),
            "ai_fallback_only": os.getenv("SIMPLIFIED_AI_FALLBACK_ONLY", "true").lower()
            in {"1", "true", "yes"},
        },
    }

    out_dir = Path(os.getenv("ARTIFACTS_DIR", "."))
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "execution-config.json").write_text(json.dumps(config, indent=2))
    print("simplified-run: wrote execution-config.json")


if __name__ == "__main__":
    simplified_run()
