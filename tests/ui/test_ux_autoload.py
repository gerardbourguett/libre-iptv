from unittest.mock import MagicMock, patch

import pytest

from src.models.channel import Channel
from src.models.profile import AVATAR_COLORS
from src.profiles.manager import ProfileManager
from src.ui.main_window import MainWindow


@pytest.fixture
def manager(tmp_path):
    return ProfileManager(base_dir=tmp_path)


@pytest.fixture
def channels():
    return [Channel(url="http://cnn.com", name="CNN", group="News")]


class TestAutoLoadOnStartup:
    def test_no_autoload_when_profile_has_no_playlist(self, manager, qtbot):
        manager.create_profile("Empty", AVATAR_COLORS[0])
        w = MainWindow(manager)
        qtbot.addWidget(w)
        assert w._channel_list.count() == 0

    def test_autoload_from_local_path(self, manager, qtbot, tmp_path):
        m3u = "#EXTM3U\n#EXTINF:-1,CNN\nhttp://cnn.com\n"
        playlist = tmp_path / "list.m3u"
        playlist.write_text(m3u, encoding="utf-8")

        manager.create_profile("P", AVATAR_COLORS[0])
        manager.update_playlist(path=str(playlist))
        manager.save_active()

        w = MainWindow(manager)
        qtbot.addWidget(w)
        assert w._channel_list.count() > 0

    def test_autoload_url_starts_fetch_worker(self, manager, qtbot):
        manager.create_profile("P", AVATAR_COLORS[0])
        manager.update_playlist(url="http://example.com/list.m3u")
        manager.save_active()

        with patch("src.ui.main_window.PlaylistFetchWorker") as MockWorker:
            instance = MagicMock()
            MockWorker.return_value = instance
            instance.fetched = MagicMock()
            instance.fetched.connect = MagicMock()
            instance.error = MagicMock()
            instance.error.connect = MagicMock()
            w = MainWindow(manager)
            qtbot.addWidget(w)
            MockWorker.assert_called_once_with("http://example.com/list.m3u")
            instance.start.assert_called_once()


class TestAutoLoadOnProfileSwitch:
    def test_switching_profile_with_local_playlist_loads_channels(
        self, manager, qtbot, tmp_path
    ):
        m3u = "#EXTM3U\n#EXTINF:-1,ESPN\nhttp://espn.com\n"
        playlist = tmp_path / "p2.m3u"
        playlist.write_text(m3u, encoding="utf-8")

        p1 = manager.create_profile("P1", AVATAR_COLORS[0])
        p2 = manager.create_profile("P2", AVATAR_COLORS[1])
        manager.switch_profile(p2.id)
        manager.update_playlist(path=str(playlist))
        manager.save_active()
        manager.switch_profile(p1.id)

        w = MainWindow(manager)
        qtbot.addWidget(w)

        # Switch to P2 — should trigger auto-load
        w._on_profile_switched(manager.switch_profile(p2.id))
        assert w._channel_list.count() > 0
