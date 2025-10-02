from pathlib import Path
import time

from scripts.cleanup_orphans import list_abandoned_locks


def test_list_abandoned_locks(tmp_path: Path) -> None:
    locks = tmp_path / ".locks"
    locks.mkdir()
    f = locks / "a.lock"
    f.write_text("pid")
    old = time.time() - 7200
    os_utime = getattr(Path, "touch", None)
    # best-effort to age the file
    import os
    os.utime(f, (old, old))
    found = list_abandoned_locks(1, base_dir=str(locks))
    assert f in found

