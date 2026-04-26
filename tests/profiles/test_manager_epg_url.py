from __future__ import annotations

from pathlib import Path

from src.models.profile import Profile
from src.profiles.manager import ProfileManager


class TestManagerEpgUrl:
    def test_epg_url_preserved_across_save_reload(self, tmp_path: Path) -> None:
        mgr = ProfileManager(base_dir=tmp_path)
        profile = mgr.create_profile("Test", "#00bcd4")
        mgr.update_epg_url(profile.id, "https://example.com/epg.xml")
        mgr.save_active()

        # Reload
        mgr2 = ProfileManager(base_dir=tmp_path)
        reloaded = mgr2.active_profile()
        assert reloaded.epg_url == "https://example.com/epg.xml"

    def test_add_to_recent_preserves_epg_url(self, tmp_path: Path) -> None:
        mgr = ProfileManager(base_dir=tmp_path)
        profile = mgr.create_profile("Test", "#00bcd4")
        mgr.update_epg_url(profile.id, "https://example.com/epg.xml")
        mgr.add_to_recent("http://ch1.com")
        assert mgr.active_profile().epg_url == "https://example.com/epg.xml"

    def test_toggle_favorite_preserves_epg_url(self, tmp_path: Path) -> None:
        mgr = ProfileManager(base_dir=tmp_path)
        profile = mgr.create_profile("Test", "#00bcd4")
        mgr.update_epg_url(profile.id, "https://example.com/epg.xml")
        mgr.toggle_favorite("http://ch1.com")
        assert mgr.active_profile().epg_url == "https://example.com/epg.xml"

    def test_update_playlist_preserves_epg_url(self, tmp_path: Path) -> None:
        mgr = ProfileManager(base_dir=tmp_path)
        profile = mgr.create_profile("Test", "#00bcd4")
        mgr.update_epg_url(profile.id, "https://example.com/epg.xml")
        mgr.update_playlist(url="https://new.com/playlist.m3u")
        assert mgr.active_profile().epg_url == "https://example.com/epg.xml"
        assert mgr.active_profile().playlist_url == "https://new.com/playlist.m3u"
