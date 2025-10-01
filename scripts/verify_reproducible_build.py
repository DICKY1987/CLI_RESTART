import hashlib
import shlex
import subprocess
import sys
from pathlib import Path

def sh(cmd: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    print(f"$ {cmd}")
    return subprocess.run(shlex.split(cmd), cwd=cwd, check=True, capture_output=True)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    dist = root / 'dist'
    if dist.exists():
        for f in dist.iterdir():
            f.unlink()
    # Build 1
    sh(f"python -m build")
    artifacts1 = sorted(dist.glob('*'))
    if not artifacts1:
        print('no artifacts after first build', file=sys.stderr)
        return 1
    hashes1 = {p.name: sha256(p) for p in artifacts1}
    # Clean and build 2
    for f in dist.iterdir():
        f.unlink()
    sh(f"python -m build")
    artifacts2 = sorted(dist.glob('*'))
    hashes2 = {p.name: sha256(p) for p in artifacts2}
    if hashes1 != hashes2:
        print('artifact hashes differ between builds', file=sys.stderr)
        print(hashes1, file=sys.stderr)
        print(hashes2, file=sys.stderr)
        return 2
    print('reproducible build verified')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())