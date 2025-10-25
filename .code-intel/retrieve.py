from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = (HERE / "..").resolve()
DB_DIR = HERE / "db"
DOCS_PATH = DB_DIR / "docs.jsonl"


@dataclass
class Config:
    ollama_url: str
    chat_model: str
    embeddings_model: str
    top_k: int
    min_score: float
    max_chars: int
    overlap_chars: int
    boost_paths: List[str]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_config() -> Config:
    cfg = read_json(HERE / "config.json")
    return Config(
        ollama_url=cfg.get("ollama_url", "http://localhost:11434"),
        chat_model=cfg.get("chat_model", "deepseek-coder"),
        embeddings_model=cfg.get("embeddings_model", "mxbai-embed-large"),
        top_k=int(cfg.get("top_k", 12)),
        min_score=float(cfg.get("min_score", 0.15)),
        max_chars=int(cfg.get("max_chars", 1200)),
        overlap_chars=int(cfg.get("overlap_chars", 200)),
        boost_paths=list(cfg.get("boost_paths", [])),
    )


def ollama_embed(url: str, model: str, text: str) -> List[float]:
    try:
        req = urllib.request.Request(
            f"{url}/api/embeddings",
            data=json.dumps({"model": model, "input": [text]}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        emb = body.get("embeddings", [[]])[0]
        return emb
    except Exception:
        return []


def cosine(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0
    s = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        s += x * y
        na += x * x
        nb += y * y
    if na <= 0 or nb <= 0:
        return 0.0
    return s / math.sqrt(na * nb)


def load_docs() -> List[dict]:
    docs: List[dict] = []
    if not DOCS_PATH.exists():
        return docs
    with open(DOCS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                docs.append(json.loads(line))
            except Exception:
                continue
    return docs


def apply_boost(path: str, base: float, boosts: List[str]) -> float:
    score = base
    for b in boosts:
        if b.endswith("/") and path.startswith(b):
            score += 0.25
        elif path.endswith(b) or path.startswith(b):
            score += 0.30
    return score


def retrieve(query: str) -> List[Tuple[float, dict]]:
    cfg = load_config()
    q_emb = ollama_embed(cfg.ollama_url, cfg.embeddings_model, query)
    docs = load_docs()
    scored: List[Tuple[float, dict]] = []
    for d in docs:
        score = cosine(q_emb, d.get("embedding", []))
        score = apply_boost(d.get("path", ""), score, cfg.boost_paths)
        if score >= cfg.min_score:
            scored.append((score, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[: cfg.top_k]


def main() -> None:
    ap = argparse.ArgumentParser(description="Retrieve relevant chunks from .code-intel index")
    ap.add_argument("--query", required=True, help="Natural language query")
    ap.add_argument("--json", action="store_true", help="Output JSON only")
    args = ap.parse_args()

    results = retrieve(args.query)
    out = [
        {
            "score": round(score, 4),
            "path": d.get("path"),
            "chunk": d.get("chunk_index"),
            "text": d.get("text"),
        }
        for score, d in results
    ]
    print(json.dumps({"results": out}, ensure_ascii=True))


if __name__ == "__main__":
    main()
