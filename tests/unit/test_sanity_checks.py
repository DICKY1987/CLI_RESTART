from __future__ import annotations

import pytest

from sanity_checks import FlagSummary, check_even_numbers, summarize_flags


def test_check_even_numbers_passes_for_even_inputs():
    assert check_even_numbers([2, 4, 6]) is True


def test_check_even_numbers_rejects_odd_inputs():
    assert check_even_numbers([2, 4, 7]) is False


def test_check_even_numbers_validates_types():
    with pytest.raises(TypeError):
        check_even_numbers([2, "three", 4])


def test_summarize_flags_reports_counts_and_ratio():
    summary = summarize_flags([True, False, True, True])

    assert summary == FlagSummary(total=4, positives=3, negatives=1)
    assert summary.ratio == pytest.approx(0.75)


def test_summarize_flags_handles_empty_input():
    summary = summarize_flags([])

    assert summary.total == 0
    assert summary.positives == 0
    assert summary.negatives == 0
    assert summary.ratio == 0.0
