from __future__ import annotations

import pytest

from src.models.profile import HistoryEntry, Profile, UserPrefs


class TestProfileParentalFields:
    def test_defaults_when_omitted(self) -> None:
        """New fields default to empty when not provided."""
        p = Profile(id="abc", name="Test", color="#00bcd4")
        assert p.pin_hash == ""
        assert p.blocked == {}

    def test_can_set_pin_hash(self) -> None:
        p = Profile(id="abc", name="Test", color="#00bcd4", pin_hash="salt$hash")
        assert p.pin_hash == "salt$hash"

    def test_can_set_blocked(self) -> None:
        blocked = {"channels": ["http://a.com"], "groups": ["News"]}
        p = Profile(id="abc", name="Test", color="#00bcd4", blocked=blocked)
        assert p.blocked == blocked


class TestProfileSerializationParental:
    def test_to_dict_includes_parental_fields(self) -> None:
        p = Profile(
            id="x",
            name="N",
            color="#ff9800",
            pin_hash="salt$hash",
            blocked={"channels": ["http://a.com"], "groups": ["X"]},
        )
        d = p.to_dict()
        assert d["pin_hash"] == "salt$hash"
        assert d["blocked"] == {"channels": ["http://a.com"], "groups": ["X"]}

    def test_from_dict_with_parental_fields(self) -> None:
        d = {
            "id": "x",
            "name": "N",
            "color": "#00bcd4",
            "pin_hash": "salt$hash",
            "blocked": {"channels": ["http://a.com"]},
        }
        p = Profile.from_dict(d)
        assert p.pin_hash == "salt$hash"
        assert p.blocked == {"channels": ["http://a.com"]}

    def test_from_dict_missing_parental_fields_use_defaults(self) -> None:
        """Backwards compatibility: old JSON without pin_hash/blocked loads fine."""
        d = {
            "id": "x",
            "name": "N",
            "color": "#00bcd4",
            "playlist_url": "",
            "playlist_path": "",
            "favorites": [],
            "recent": [],
            "last_channel_url": "",
        }
        p = Profile.from_dict(d)
        assert p.pin_hash == ""
        assert p.blocked == {}

    def test_roundtrip_with_parental_fields(self) -> None:
        p = Profile(
            id="abc-123",
            name="Mi Lista",
            color="#4caf50",
            pin_hash="salty$deadbeef",
            blocked={"channels": ["http://cnn.com"], "groups": ["News"]},
        )
        restored = Profile.from_dict(p.to_dict())
        assert restored == p


class TestHistoryEntry:
    def test_basic_fields(self) -> None:
        entry = HistoryEntry(channel_id="abc123", watched_at="2026-04-26T12:00:00Z", duration_s=3600)
        assert entry.channel_id == "abc123"
        assert entry.watched_at == "2026-04-26T12:00:00Z"
        assert entry.duration_s == 3600

    def test_defaults(self) -> None:
        entry = HistoryEntry(channel_id="abc123")
        assert entry.channel_id == "abc123"
        assert entry.watched_at == ""
        assert entry.duration_s == 0


class TestUserPrefs:
    def test_defaults(self) -> None:
        prefs = UserPrefs()
        assert prefs.theme == "midnight"
        assert prefs.accent_color == ""
        assert prefs.volume == 100
        assert prefs.subtitle_lang == ""
        assert prefs.last_channel == ""

    def test_custom_values(self) -> None:
        prefs = UserPrefs(theme="dark", accent_color="#ff0000", volume=80, subtitle_lang="es", last_channel="ch1")
        assert prefs.theme == "dark"
        assert prefs.accent_color == "#ff0000"
        assert prefs.volume == 80
        assert prefs.subtitle_lang == "es"
        assert prefs.last_channel == "ch1"


class TestProfileHistoryAndPrefs:
    def test_history_defaults_empty(self) -> None:
        p = Profile(id="x", name="N", color="#00bcd4")
        assert p.history == []

    def test_prefs_defaults(self) -> None:
        p = Profile(id="x", name="N", color="#00bcd4")
        assert p.prefs.theme == "midnight"
        assert p.prefs.volume == 100

    def test_can_set_history(self) -> None:
        hist = [HistoryEntry(channel_id="abc", watched_at="2026-04-26T12:00:00Z", duration_s=300)]
        p = Profile(id="x", name="N", color="#00bcd4", history=hist)
        assert p.history == hist

    def test_can_set_prefs(self) -> None:
        prefs = UserPrefs(theme="light", volume=50)
        p = Profile(id="x", name="N", color="#00bcd4", prefs=prefs)
        assert p.prefs.theme == "light"
        assert p.prefs.volume == 50


class TestProfileSerializationHistoryPrefs:
    def test_to_dict_includes_history_and_prefs(self) -> None:
        hist = [HistoryEntry(channel_id="abc", watched_at="2026-04-26T12:00:00Z", duration_s=300)]
        prefs = UserPrefs(theme="dark", volume=75)
        p = Profile(id="x", name="N", color="#00bcd4", history=hist, prefs=prefs)
        d = p.to_dict()
        assert d["history"] == [{"channel_id": "abc", "watched_at": "2026-04-26T12:00:00Z", "duration_s": 300}]
        assert d["prefs"] == {"theme": "dark", "accent_color": "", "volume": 75, "subtitle_lang": "", "last_channel": "", "last_screen": "home"}

    def test_from_dict_with_history_and_prefs(self) -> None:
        d = {
            "id": "x",
            "name": "N",
            "color": "#00bcd4",
            "history": [{"channel_id": "abc", "watched_at": "2026-04-26T12:00:00Z", "duration_s": 300}],
            "prefs": {"theme": "dark", "volume": 75},
        }
        p = Profile.from_dict(d)
        assert len(p.history) == 1
        assert p.history[0].channel_id == "abc"
        assert p.prefs.theme == "dark"
        assert p.prefs.volume == 75

    def test_from_dict_missing_history_and_prefs_uses_defaults(self) -> None:
        """REQ-07: Legacy JSON without history/prefs loads with defaults."""
        d = {
            "id": "x",
            "name": "N",
            "color": "#00bcd4",
            "playlist_url": "",
            "playlist_path": "",
            "favorites": [],
            "recent": [],
            "last_channel_url": "",
        }
        p = Profile.from_dict(d)
        assert p.history == []
        assert p.prefs.theme == "midnight"
        assert p.prefs.volume == 100

    def test_roundtrip_with_history_and_prefs(self) -> None:
        hist = [HistoryEntry(channel_id="abc", watched_at="2026-04-26T12:00:00Z", duration_s=300)]
        prefs = UserPrefs(theme="dark", volume=75)
        p = Profile(id="x", name="N", color="#00bcd4", history=hist, prefs=prefs)
        restored = Profile.from_dict(p.to_dict())
        assert restored == p
