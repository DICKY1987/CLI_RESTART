from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

import urllib.request

HERE = Path(__file__).resolve().parent


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def chat(ollama_url: str, model: str, messages: List[dict]) -> str:
    req = urllib.request.Request(
        f"{ollama_url}/api/chat",
        data=json.dumps({"model": model, "messages": messages, "stream": False}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body.get("message", {}).get("content", "")


def main() -> None:
    ap = argparse.ArgumentParser(description="Ask DeepSeek with retrieved context")
    ap.add_argument("--question", required=True)
    ap.add_argument("--context_json", help="JSON from retrieve.py (optional)")
    args = ap.parse_args()

    cfg = read_json(HERE / "config.json")
    context_text = ""
    if args.context_json and Path(args.context_json).exists():
        data = json.loads(Path(args.context_json).read_text(encoding="utf-8"))
        parts = []
        for r in data.get("results", [])[: cfg.get("top_k", 12)]:
            parts.append(f"# {r.get('path')}:{r.get('chunk')}\n{r.get('text')}")
        context_text = "\n\n".join(parts)

    system = (
        "You are an expert software engineer. Use the provided repository context "
        "to answer precisely. If uncertain, state assumptions clearly."
    )
    user = (
        ("Context:\n\n" + context_text + "\n\n") if context_text else ""
    ) + f"Question: {args.question}"

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    answer = chat(cfg.get("ollama_url", "http://localhost:11434"), cfg.get("chat_model", "deepseek-coder"), messages)
    print(answer)


if __name__ == "__main__":
    main()

