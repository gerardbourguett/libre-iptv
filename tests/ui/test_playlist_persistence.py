import json
from unittest.mock import MagicMock, patch

import pytest

from src.models.profile import AVATAR_COLORS
from src.profiles.manager import ProfileManager
from src.ui.main_window import MainWindow


@pytest.fixture
def manager(tmp_path):
    mgr = ProfileManager(base_dir=tmp_path)
    mgr.create_profile("Test", AVATAR_COLORS[0])
    return mgr


@pytest.fixture
def window(manager, qtbot):
    w = MainWindow(manager)
    qtbot.addWidget(w)
    return w


class TestPlaylistPersistence:
    def test_open_playlist_file_saves_path_to_profile(
        self, window, manager, tmp_path
    ):
        m3u = "#EXTM3U\n#EXTINF:-1,CNN\nhttp://cnn.com\n"
        playlist = tmp_path / "list.m3u"
        playlist.write_text(m3u, encoding="utf-8")

        with patch(
            "src.ui.main_window.QFileDialog.getOpenFileName",
            return_value=(str(playlist), ""),
        ):
            window._open_playlist()

        assert manager.active_profile().playlist_path == str(playlist)

    def test_open_playlist_file_persists_to_disk(
        self, window, manager, tmp_path
    ):
        m3u = "#EXTM3U\n#EXTINF:-1,CNN\nhttp://cnn.com\n"
        playlist = tmp_path / "list.m3u"
        playlist.write_text(m3u, encoding="utf-8")

        with patch(
            "src.ui.main_window.QFileDialog.getOpenFileName",
            return_value=(str(playlist), ""),
        ):
            window._open_playlist()

        pid = manager.active_profile().id
        data = json.loads((tmp_path / f"{pid}.json").read_text())
        assert data["playlist_path"] == str(playlist)

    def test_open_playlist_updates_channels_in_memory(
        self, window, manager, tmp_path
    ):
        m3u = "#EXTM3U\n#EXTINF:-1,CNN\nhttp://cnn.com\n"
        playlist = tmp_path / "list.m3u"
        playlist.write_text(m3u, encoding="utf-8")

        with patch(
            "src.ui.main_window.QFileDialog.getOpenFileName",
            return_value=(str(playlist), ""),
        ):
            window._open_playlist()

        assert len(window._channels) == 1
        assert window._channels[0].name == "CNN"

    def test_open_url_saves_url_to_profile(self, window, manager):
        with patch(
            "src.ui.main_window.QInputDialog.getText",
            return_value=("http://example.com/list.m3u", True),
        ), patch("src.services.playlist_service.PlaylistFetchWorker") as MockWorker:
            instance = MagicMock()
            MockWorker.return_value = instance
            instance.fetched = MagicMock()
            instance.fetched.connect = MagicMock()
            instance.error = MagicMock()
            instance.error.connect = MagicMock()
            window._open_url()

        assert manager.active_profile().playlist_url == "http://example.com/list.m3u"
