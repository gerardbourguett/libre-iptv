from unittest.mock import MagicMock, patch

import pytest

from src.i18n import init_translator
from src.models.channel import Channel
from src.models.profile import AVATAR_COLORS
from src.profiles.manager import ProfileManager
from src.ui.main_window import MainWindow
from src.ui.profile_bar import ProfileSelectorBar


@pytest.fixture(autouse=True)
def reset_vlc_manager():
    from src.core.vlc_manager import VlcManager

    VlcManager._instance = None
    yield


@pytest.fixture(autouse=True)
def translator(qapp):
    init_translator(locales_dir=None)


@pytest.fixture
def mock_vlc():
    with patch("src.ui.player_widget.vlc") as mock, patch(
        "src.core.vlc_manager.vlc"
    ) as mock_mgr:
        instance = MagicMock()
        player = MagicMock()
        mock.Instance.return_value = instance
        mock_mgr.Instance.return_value = instance
        instance.media_player_new.return_value = player
        yield mock, player


@pytest.fixture
def manager(tmp_path):
    mgr = ProfileManager(base_dir=tmp_path)
    mgr.create_profile("Test", AVATAR_COLORS[0])
    return mgr


@pytest.fixture
def window(manager, qtbot, mock_vlc):
    w = MainWindow(manager)
    qtbot.addWidget(w)
    return w


class TestMainWindowAcceptsManager:
    def test_window_has_profile_bar(self, window):
        bar = window.findChild(ProfileSelectorBar)
        assert bar is not None

    def test_profile_bar_shows_active_profile(self, window, manager):
        bar = window.findChild(ProfileSelectorBar)
        assert bar is not None
        assert manager.active_profile().name in bar.profile_name_text()


class TestChannelSelectedAddsToRecent:
    def test_channel_selected_adds_to_recent(self, window, manager):
        channel = Channel(url="http://cnn.com", name="CNN", group="News")
        window._on_channel_selected(channel)
        assert "http://cnn.com" in manager.active_profile().recent

    def test_channel_selected_saves_active_profile(
        self, window, manager, tmp_path
    ):
        import json
        channel = Channel(url="http://bbc.com", name="BBC", group="News")
        window._on_channel_selected(channel)
        pid = manager.active_profile().id
        data = json.loads((tmp_path / f"{pid}.json").read_text())
        assert "http://bbc.com" in data["recent"]


class TestCloseEventSavesProfile:
    def test_close_event_saves_active_profile(self, window, manager, tmp_path):
        import json
        manager.add_to_recent("http://espn.com")
        window.close()
        pid = manager.active_profile().id
        data = json.loads((tmp_path / f"{pid}.json").read_text())
        assert "http://espn.com" in data["recent"]
