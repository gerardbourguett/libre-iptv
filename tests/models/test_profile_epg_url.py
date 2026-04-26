from __future__ import annotations

from src.models.profile import Profile


class TestProfileEpgUrl:
    def test_defaults_to_empty(self) -> None:
        p = Profile(id="abc", name="Test", color="#00bcd4")
        assert p.epg_url == ""

    def test_can_set_epg_url(self) -> None:
        p = Profile(id="abc", name="Test", color="#00bcd4", epg_url="https://example.com/epg.xml")
        assert p.epg_url == "https://example.com/epg.xml"

    def test_to_dict_includes_epg_url(self) -> None:
        p = Profile(id="x", name="N", color="#ff9800", epg_url="https://a.com/epg.xml")
        d = p.to_dict()
        assert d["epg_url"] == "https://a.com/epg.xml"

    def test_from_dict_with_epg_url(self) -> None:
        d = {
            "id": "x",
            "name": "N",
            "color": "#00bcd4",
            "epg_url": "https://b.com/epg.xml",
        }
        p = Profile.from_dict(d)
        assert p.epg_url == "https://b.com/epg.xml"

    def test_from_dict_missing_epg_url_uses_default(self) -> None:
        """Backwards compatibility: old JSON without epg_url loads fine."""
        d = {
            "id": "x",
            "name": "N",
            "color": "#00bcd4",
            "playlist_url": "",
            "playlist_path": "",
            "favorites": [],
            "recent": [],
            "last_channel_url": "",
            "pin_hash": "",
            "blocked": {},
        }
        p = Profile.from_dict(d)
        assert p.epg_url == ""

    def test_roundtrip(self) -> None:
        p = Profile(
            id="abc-123",
            name="Mi Lista",
            color="#4caf50",
            epg_url="https://example.com/epg.xml",
        )
        restored = Profile.from_dict(p.to_dict())
        assert restored == p
