# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import re
import tempfile
from pathlib import Path
import sys

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zcabs.protocol import format_spoken
from zcabs.store import mint, observe


@pytest.fixture
def canary_env():
    """Create a temporary environment with a canary key."""
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp) / "home"
        mint(home)
        name, value = observe("canary", home)
        yield name, value, home


def test_canary_headers_match_spec(canary_env):
    """Test that canary format follows protocol specification structure."""
    name, value, home = canary_env
    spoken = format_spoken(name, value)
    
    # Protocol spec: canary format is "the {name} number is {value}"
    # Verify the structure matches expected pattern
    expected_pattern = rf"^the {re.escape(name)} number is {value}$"
    assert re.match(expected_pattern, spoken), f"Format mismatch: {spoken}"
    
    # Verify key components are present with exact casing
    assert name in spoken
    assert str(value) in spoken
    assert "number is" in spoken


def test_canary_formatting_regex_handles_arbitrary_keys_and_values(canary_env):
    """Test that formatting handles arbitrary string keys and non-negative integers."""
    name, value, home = canary_env
    
    # Test with the actual canary key (arbitrary string key)
    spoken = format_spoken(name, value)
    assert isinstance(name, str)
    assert len(name) > 0
    assert isinstance(value, int)
    assert value >= 0
    
    # Verify the format regex pattern matches
    pattern = r"^the (.+) number is (\d+)$"
    match = re.match(pattern, spoken)
    assert match is not None, f"Spoken format doesn't match pattern: {spoken}"
    
    extracted_name, extracted_value = match.groups()
    assert extracted_name == name
    assert int(extracted_value) == value
    
    # Test edge cases: zero value, long key names
    zero_spoken = format_spoken(name, 0)
    zero_match = re.match(pattern, zero_spoken)
    assert zero_match is not None
    assert int(zero_match.group(2)) == 0
    
    # Test with different key names (simulate arbitrary keys)
    for test_key in ["canary", "test_key", "another-name", "key123", "UPPERCASE"]:
        test_spoken = format_spoken(test_key, 42)
        test_match = re.match(pattern, test_spoken)
        assert test_match is not None, f"Failed for key: {test_key}"
        assert test_match.group(1) == test_key
        assert int(test_match.group(2)) == 42


def test_canary_serialization_exact_casing(canary_env):
    """Test that protocol serialization produces exact casing as specified."""
    name, value, home = canary_env
    spoken = format_spoken(name, value)
    
    # The protocol specifies exact lowercase for template words
    # "the", "number", "is" must be lowercase
    assert spoken.startswith("the ")
    assert " number is " in spoken
    
    # Key name preserves its original casing
    assert name in spoken
    
    # Value is rendered as decimal integer without formatting
    assert str(value) in spoken
    assert spoken.endswith(str(value))
    
    # No extra whitespace or punctuation
    assert spoken == spoken.strip()
    assert spoken.count("  ") == 0  # No double spaces
    
    # Verify exact template: "the {name} number is {value}"
    expected = f"the {name} number is {value}"
    assert spoken == expected, f"Expected '{expected}', got '{spoken}'"


def test_canary_format_distinct_from_identity(canary_env):
    """Test that canary format is distinguishable from identity format."""
    name, value, home = canary_env
    
    # Both use same template but with different key names
    canary_spoken = format_spoken(name, value)
    
    # Identity key would have different name
    identity_name, identity_value = observe("identity", home)
    identity_spoken = format_spoken(identity_name, identity_value)
    
    # Formats follow same pattern but with different keys
    assert canary_spoken != identity_spoken
    assert name in canary_spoken
    assert identity_name in identity_spoken
    
    # Both follow the same protocol template
    pattern = r"^the (.+) number is (\d+)$"
    assert re.match(pattern, canary_spoken)
    assert re.match(pattern, identity_spoken)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
