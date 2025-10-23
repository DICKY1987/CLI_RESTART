"""Lightweight helpers that allow the unit-test suite to validate coverage wiring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class FlagSummary:
    """Summary information derived from a sequence of boolean flags."""

    total: int
    positives: int
    negatives: int

    @property
    def ratio(self) -> float:
        """Return the fraction of positive flags.

        The calculation guards against division by zero so that an empty
        sequence simply reports a neutral ratio of ``0.0``.
        """

        if self.total == 0:
            return 0.0
        return self.positives / self.total


def check_even_numbers(values: Iterable[int]) -> bool:
    """Return ``True`` when every provided integer is even.

    The function intentionally performs two passes: the first validates that
    every entry is an integer, while the second checks the parity.  The split
    keeps the logic straightforward for unit tests which assert both the happy
    path and individual failure conditions.
    """

    numbers = list(values)
    if any(not isinstance(value, int) for value in numbers):
        raise TypeError("All values must be integers")

    return all(value % 2 == 0 for value in numbers)


def summarize_flags(flags: Iterable[bool]) -> FlagSummary:
    """Build a :class:`FlagSummary` describing the boolean values observed."""

    total = 0
    positives = 0
    for flag in flags:
        total += 1
        if flag:
            positives += 1

    negatives = total - positives
    return FlagSummary(total=total, positives=positives, negatives=negatives)
