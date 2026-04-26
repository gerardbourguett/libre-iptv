from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from src.core.parental import get_blocked_sets, hash_pin, is_channel_blocked, verify_pin
from src.models.channel import Channel


@dataclass
class _FakeProfile:
    """Minimal stand-in for Profile with parental fields."""

    pin_hash: str = ""
    blocked: dict[str, list[str]] = field(default_factory=dict)


class TestHashPin:
    def test_returns_salt_hash_format(self) -> None:
        """Hash format is 'salt$hexdigest'."""
        result = hash_pin("1234")
        parts = result.split("$")
        assert len(parts) == 2
        salt, hexdigest = parts
        assert len(salt) > 0
        assert len(hexdigest) == 64  # SHA-256 hex

    def test_same_pin_same_salt_same_hash(self) -> None:
        """Deterministic when salt is provided."""
        salt = "abc123"
        h1 = hash_pin("1234", salt=salt)
        h2 = hash_pin("1234", salt=salt)
        assert h1 == h2

    def test_different_salts_different_hashes(self) -> None:
        """Salt uniqueness produces different hashes."""
        h1 = hash_pin("1234", salt="salt1")
        h2 = hash_pin("1234", salt="salt2")
        assert h1 != h2

    def test_auto_generated_salt_is_random(self) -> None:
        """When salt omitted, two calls produce different salts."""
        h1 = hash_pin("1234")
        h2 = hash_pin("1234")
        salt1 = h1.split("$")[0]
        salt2 = h2.split("$")[0]
        assert salt1 != salt2


class TestVerifyPin:
    def test_correct_pin_verifies(self) -> None:
        """verify_pin returns True for the correct PIN."""
        stored = hash_pin("5678")
        assert verify_pin("5678", stored) is True

    def test_wrong_pin_fails(self) -> None:
        """verify_pin returns False for an incorrect PIN."""
        stored = hash_pin("5678")
        assert verify_pin("0000", stored) is False

    def test_empty_stored_hash_fails(self) -> None:
        """verify_pin returns False when no PIN is set."""
        assert verify_pin("1234", "") is False

    def test_different_pin_same_format_fails(self) -> None:
        """Another 4-digit PIN does not verify."""
        stored = hash_pin("1234")
        assert verify_pin("1235", stored) is False


class TestIsChannelBlocked:
    def test_blocked_by_url(self) -> None:
        """Channel is blocked when its URL is in blocked.channels."""
        profile = _FakeProfile(
            pin_hash="salt$hash",
            blocked={"channels": ["http://cnn.com"], "groups": []},
        )
        ch = Channel(url="http://cnn.com", name="CNN", group="News")
        assert is_channel_blocked(ch, profile) is True

    def test_blocked_by_group(self) -> None:
        """Channel is blocked when its group is in blocked.groups."""
        profile = _FakeProfile(
            pin_hash="salt$hash",
            blocked={"channels": [], "groups": ["Sports"]},
        )
        ch = Channel(url="http://espn.com", name="ESPN", group="Sports")
        assert is_channel_blocked(ch, profile) is True

    def test_not_blocked(self) -> None:
        """Channel is not blocked when neither URL nor group is blocked."""
        profile = _FakeProfile(
            pin_hash="salt$hash",
            blocked={"channels": ["http://cnn.com"], "groups": ["Sports"]},
        )
        ch = Channel(url="http://bbc.com", name="BBC", group="News")
        assert is_channel_blocked(ch, profile) is False

    def test_blocked_by_both(self) -> None:
        """Channel blocked by both URL and group still returns True."""
        profile = _FakeProfile(
            pin_hash="salt$hash",
            blocked={"channels": ["http://espn.com"], "groups": ["Sports"]},
        )
        ch = Channel(url="http://espn.com", name="ESPN", group="Sports")
        assert is_channel_blocked(ch, profile) is True

    def test_empty_blocklist_never_blocks(self) -> None:
        """Profile with empty blocked dict never blocks."""
        profile = _FakeProfile(pin_hash="salt$hash", blocked={})
        ch = Channel(url="http://cnn.com", name="CNN", group="News")
        assert is_channel_blocked(ch, profile) is False


class TestGetBlockedSets:
    def test_returns_frozensets(self) -> None:
        """Result is a tuple of two frozensets."""
        profile = _FakeProfile(
            blocked={"channels": ["a", "b"], "groups": ["News"]},
        )
        urls, groups = get_blocked_sets(profile)
        assert isinstance(urls, frozenset)
        assert isinstance(groups, frozenset)

    def test_empty_profile_returns_empty_sets(self) -> None:
        """Missing or empty blocked yields empty frozensets."""
        profile = _FakeProfile(blocked={})
        urls, groups = get_blocked_sets(profile)
        assert urls == frozenset()
        assert groups == frozenset()

    def test_extracts_channels_and_groups(self) -> None:
        """Correctly extracts blocked URLs and group names."""
        profile = _FakeProfile(
            blocked={"channels": ["http://a.com", "http://b.com"], "groups": ["X", "Y"]},
        )
        urls, groups = get_blocked_sets(profile)
        assert urls == frozenset(["http://a.com", "http://b.com"])
        assert groups == frozenset(["X", "Y"])

    def test_missing_keys_return_empty(self) -> None:
        """Partial blocked dict yields empty set for missing key."""
        profile = _FakeProfile(blocked={"channels": ["http://a.com"]})
        urls, groups = get_blocked_sets(profile)
        assert urls == frozenset(["http://a.com"])
        assert groups == frozenset()
