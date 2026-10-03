# tests/test_token_ttl.py
from __future__ import annotations

import pytest


def is_token_valid(created_at, ttl_seconds, current_time, clock_skew: int = 2) -> bool:
    """Determine if a token is valid based on creation time, TTL, and clock skew.

    Returns:
        True:  within TTL window (and within clock skew tolerance if current_time < created_at)
        False: expired (current_time > created_at + ttl_seconds)
        False: timestamp in the future beyond clock skew tolerance
                 (current_time < created_at - clock_skew)
    """
    # Expired: current time past the TTL window
    if current_time > created_at + ttl_seconds:
        return False
    # Future beyond clock skew tolerance: creation time is ahead of current time
    # by more than the allowed clock skew
    if current_time < created_at - clock_skew:
        return False
    # Within TTL window (including slight future within clock skew tolerance)
    return True


class TestTokenTTL:
    def test_within_ttl_window(self):
        # Token created at 1000, TTL 60s, current at 1000 → True (start of window)
        assert is_token_valid(created_at=1000, ttl_seconds=60, current_time=1000) is True
        # Current near the end of the TTL window → True
        assert is_token_valid(created_at=1000, ttl_seconds=60, current_time=1059) is True

    def test_expired(self):
        # Current just past TTL expiry → False
        assert is_token_valid(created_at=1000, ttl_seconds=60, current_time=1061) is False
        # Current far past expiry → False
        assert is_token_valid(created_at=1000, ttl_seconds=60, current_time=2000) is False

    def test_future_beyond_clock_skew(self):
        # Current 19 seconds before creation (skew=2) → False (beyond tolerance)
        assert is_token_valid(created_at=1000, ttl_seconds=60, current_time=979) is False
        # Current 1 second before creation (within skew=2) → True (within tolerance)
        assert is_token_valid(created_at=1000, ttl_seconds=60, current_time=999) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
