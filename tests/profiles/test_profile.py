import pytest

from src.models.profile import AVATAR_COLORS, Profile


class TestProfileDefaults:
    def test_required_fields(self):
        p = Profile(id="abc", name="Test", color="#00bcd4")
        assert p.id == "abc"
        assert p.name == "Test"
        assert p.color == "#00bcd4"

    def test_optional_fields_default_empty(self):
        p = Profile(id="abc", name="Test", color="#00bcd4")
        assert p.playlist_url == ""
        assert p.playlist_path == ""
        assert p.favorites == []
        assert p.recent == []
        assert p.last_channel_url == ""
        assert p.pin_hash == ""
        assert p.blocked == {}

    def test_to_dict_roundtrip(self):
        p = Profile(
            id="abc-123",
            name="Mi Lista",
            color="#4caf50",
            playlist_url="http://example.com/list.m3u",
            playlist_path="",
            favorites=["http://cnn.com"],
            recent=["http://bbc.com", "http://espn.com"],
            last_channel_url="http://bbc.com",
        )
        restored = Profile.from_dict(p.to_dict())
        assert restored == p

    def test_to_dict_contains_all_fields(self):
        p = Profile(id="x", name="N", color="#ff9800")
        d = p.to_dict()
        assert set(d.keys()) == {
            "id", "name", "color",
            "playlist_url", "playlist_path",
            "favorites", "recent", "last_channel_url",
            "pin_hash", "blocked", "epg_url",
            "history", "prefs",
        }

    def test_from_dict_missing_optional_fields_use_defaults(self):
        d = {"id": "x", "name": "N", "color": "#00bcd4"}
        p = Profile.from_dict(d)
        assert p.favorites == []
        assert p.recent == []
        assert p.playlist_url == ""
        assert p.last_channel_url == ""
        assert p.pin_hash == ""
        assert p.blocked == {}
        assert p.epg_url == ""


class TestProfileSerialization:
    def test_to_dict_roundtrip(self):
        p = Profile(
            id="abc-123",
            name="Mi Lista",
            color="#4caf50",
            playlist_url="http://example.com/list.m3u",
            playlist_path="",
            favorites=["http://cnn.com"],
            recent=["http://bbc.com", "http://espn.com"],
            last_channel_url="http://bbc.com",
        )
        restored = Profile.from_dict(p.to_dict())
        assert restored == p

    def test_to_dict_contains_all_fields(self):
        p = Profile(id="x", name="N", color="#ff9800")
        d = p.to_dict()
        assert set(d.keys()) == {
            "id", "name", "color",
            "playlist_url", "playlist_path",
            "favorites", "recent", "last_channel_url",
            "pin_hash", "blocked", "epg_url",
            "history", "prefs",
        }

    def test_from_dict_missing_optional_fields_use_defaults(self):
        d = {"id": "x", "name": "N", "color": "#00bcd4"}
        p = Profile.from_dict(d)
        assert p.favorites == []
        assert p.recent == []
        assert p.playlist_url == ""
        assert p.last_channel_url == ""
        assert p.pin_hash == ""
        assert p.blocked == {}

    def test_from_dict_missing_required_field_raises(self):
        with pytest.raises((KeyError, TypeError)):
            Profile.from_dict({"id": "x", "name": "N"})  # missing color


class TestAvatarColors:
    def test_avatar_colors_has_six_options(self):
        assert len(AVATAR_COLORS) == 6

    def test_cyan_is_first(self):
        assert AVATAR_COLORS[0] == "#00bcd4"

    def test_all_colors_are_valid_hex(self):
        for color in AVATAR_COLORS:
            assert color.startswith("#")
            assert len(color) == 7
