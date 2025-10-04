from __future__ import annotations

"""
Legacy idempotency state helpers.

Maintains backward-compatible APIs and provides access to generic idempotency store.
"""

from typing import Set, Tuple

# Legacy API retained for compatibility with previous integrations
_seen: Set[Tuple[str, str, str, int]] = set()


def mark_seen(account: str, symbol: str, strategy: str, nonce: int) -> bool:
    key = (account, symbol, strategy, nonce)
    if key in _seen:
        return False
    _seen.add(key)
    return True
