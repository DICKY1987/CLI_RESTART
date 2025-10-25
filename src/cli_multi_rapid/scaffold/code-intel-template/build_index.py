from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import urllib.request


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


HERE = Path(__file__).resolve().parent
ROOT = (HERE / "..").resolve()
DB_DIR = HERE / "db"
DOCS_PATH = DB_DIR / "docs.jsonl"
CACHE_DIR = HERE / "cache"


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


def load_ignore_globs() -> List[str]:
    p = HERE / "ignore_globs.txt"
    if not p.exists():
        return []
    return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]


def should_ignore(rel: Path, ignore_globs: List[str]) -> bool:
    rp = rel.as_posix()
    for patt in ignore_globs:
        if patt.endswith("/") and rp.startswith(patt):
            return True
        # naive glob-ish match
        pat = re.escape(patt).replace(r"\*\*", ".*").replace(r"\*", "[^"]*")
        if re.fullmatch(pat, rp):
            return True
    return False


def iter_source_files(root: Path, include_ext: List[str], ignore_globs: List[str]):
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        rel = p.relative_to(root)
        if should_ignore(rel, ignore_globs):
            continue
        if include_ext and p.suffix.lower() not in include_ext:
            continue
        try:
            with open(p, "rb") as f:
                chunk = f.read(2048)
            if b"\0" in chunk:
                continue
        except Exception:
            continue
        yield p


def chunk_text(text: str, max_chars: int, overlap: int):
    if max_chars <= 0:
        return [text]
    chunks = []
    i = 0
    n = len(text)
    while i < n:
        j = min(i + max_chars, n)
        chunks.append(text[i:j])
        if j == n:
            break
        i = max(0, j - overlap)
    return chunks


def ollama_embeddings(url: str, model: str, inputs: List[str]) -> List[List[float]]:
    req = urllib.request.Request(
        f"{url}/api/embeddings",
        data=json.dumps({"model": model, "input": inputs}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body.get("embeddings", [])


def ensure_dirs() -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def try_build_ctags(root: Path) -> None:
    tags_path = CACHE_DIR / "tags"
    try:
        exe = "ctags.exe" if os.name == "nt" else "ctags"
        subprocess.run(
            [exe, "-R", "--languages=PowerShell,Python,JavaScript,TypeScript", "--fields=+n", "-f", str(tags_path), str(root)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def hash_id(path: Path, idx: int, text: str) -> str:
    h = hashlib.sha256()
    h.update(str(path).encode("utf-8"))
    h.update(str(idx).encode("utf-8"))
    h.update(text.encode("utf-8", errors="ignore"))
    return h.hexdigest()


def build_index(no_embed: bool = False, include_ext: Optional[list[str]] = None) -> None:
    cfg = load_config()
    ensure_dirs()
    try_build_ctags(ROOT)

    include = include_ext or [
        ".ps1",
        ".psm1",
        ".psd1",
        ".py",
        ".ts",
        ".tsx",
        ".js",
        ".json",
        ".md",
        ".yml",
        ".yaml",
        ".sh",
        ".bat",
    ]
    ignore = load_ignore_globs()

    files = list(iter_source_files(ROOT, include, ignore))
    docs: list[dict] = []

    for p in files:
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        chunks = chunk_text(text, cfg.max_chars, cfg.overlap_chars)
        for i, ch in enumerate(chunks):
            docs.append({
                "id": hash_id(p.relative_to(ROOT), i, ch),
                "path": p.relative_to(ROOT).as_posix(),
                "chunk_index": i,
                "text": ch,
            })

    embeddings: list[list[float]] = []
    if not no_embed and docs:
        inputs = [d["text"] for d in docs]
        batch_size = 64
        for i in range(0, len(inputs), batch_size):
            batch = inputs[i:i + batch_size]
            try:
                embs = ollama_embeddings(cfg.ollama_url, cfg.embeddings_model, batch)
            except Exception:
                embs = [[] for _ in batch]
            embeddings.extend(embs)

    with open(DOCS_PATH, "w", encoding="utf-8") as f:
        for idx, d in enumerate(docs):
            if embeddings:
                d["embedding"] = embeddings[idx] if idx < len(embeddings) else []
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    print(f"Wrote index: {DOCS_PATH} ({len(docs)} chunks)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Build .code-intel embeddings index")
    ap.add_argument("--no-embed", action="store_true", help="Skip embedding generation")
    args = ap.parse_args()
    build_index(no_embed=args.no_embed)


if __name__ == "__main__":
    main()

