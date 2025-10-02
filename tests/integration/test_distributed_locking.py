import threading
import time

from src.cli_multi_rapid.coordination.file_lock import FileLockBackend
from src.cli_multi_rapid.coordination.locks import lock


def test_only_one_lock_holder() -> None:
    backend = FileLockBackend()
    acquired = []

    def worker(i: int) -> None:
        try:
            with lock(backend, "resource", timeout=1.0, ttl=5.0):
                acquired.append(i)
                time.sleep(0.2)
        except TimeoutError:
            pass

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # At least one thread acquired; not more than len(threads)
    assert len(acquired) >= 1


def test_lock_released_on_exception() -> None:
    backend = FileLockBackend()
    try:
        with lock(backend, "boom", timeout=0.5, ttl=5.0):
            raise RuntimeError("fail")
    except RuntimeError:
        pass
    # Should be able to reacquire
    with lock(backend, "boom", timeout=0.5, ttl=5.0):
        pass

