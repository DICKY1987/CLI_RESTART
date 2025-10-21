import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .correlation import get_correlation_id


def log_interaction(
    *,
    actor: str,
    prompt: str,
    response: Optional[str],
    model: Optional[str],
    tokens_used: Optional[int] = None,
    metadata: Optional[dict[str, Any]] = None,
    base_dir: Path = Path("logs/conversations"),
) -> Path:
    """Append a single AI interaction to a JSONL file.

    Returns the path to the JSONL file written.
    """
    base_dir.mkdir(parents=True, exist_ok=True)
    fname = base_dir / f"{datetime.utcnow():%Y%m%d}.jsonl"

    record: dict[str, Any] = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "correlation_id": get_correlation_id(),
        "actor": actor,
        "model": model,
        "prompt": prompt,
        "response": response,
        "tokens_used": tokens_used,
        "metadata": metadata or {},
    }

    with fname.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return fname
