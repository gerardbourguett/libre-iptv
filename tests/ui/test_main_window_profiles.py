import pytest

from src.models.channel import Channel
from src.models.profile import AVATAR_COLORS
from src.profiles.manager import ProfileManager
from src.ui.main_window import MainWindow
from src.ui.profile_bar import ProfileSelectorBar


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
