from __future__ import annotations

import os
import time
from pathlib import Path

from .locks import LockBackend


class FileLockBackend(LockBackend):
    def __init__(self, base_dir: str | Path = ".locks") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _lock_path(self, name: str) -> Path:
        safe = name.replace("/", "_").replace("\\", "_")
        return self.base_dir / f"{safe}.lock"

    def acquire(self, name: str, *, timeout: float | None = None, ttl: float | None = None, retry_interval: float = 0.1) -> bool:
        path = self._lock_path(name)
        start = time.time()
        while True:
            if path.exists() and ttl is not None:
                try:
                    mtime = path.stat().st_mtime
                    if (time.time() - mtime) > ttl:
                        path.unlink(missing_ok=True)
                except FileNotFoundError:
                    pass
            try:
                fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                try:
                    os.write(fd, str(os.getpid()).encode("utf-8"))
                finally:
                    os.close(fd)
                return True
            except FileExistsError:
                if timeout is not None and (time.time() - start) >= timeout:
                    return False
                time.sleep(retry_interval)

    def release(self, name: str) -> None:
        path = self._lock_path(name)
        try:
            path.unlink(missing_ok=True)
        except PermissionError:
            for _ in range(3):
                time.sleep(0.05)
                try:
                    path.unlink(missing_ok=True)
                    break
                except PermissionError:
                    continue

