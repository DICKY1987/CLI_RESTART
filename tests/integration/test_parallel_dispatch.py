from scripts.parallel_dispatch import run_parallel


def test_parallel_runs() -> None:
    def t(n):
        return n * n

    tasks = [lambda n=n: t(n) for n in range(5)]
    results = run_parallel(tasks, workers=3)
    assert sorted(results) == [0, 1, 4, 9, 16]

