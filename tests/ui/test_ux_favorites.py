import pytest

from src.models.channel import Channel
from src.models.profile import AVATAR_COLORS
from src.profiles.manager import ProfileManager
from src.ui.channel_list import ChannelListWidget


@pytest.fixture
def manager(tmp_path):
    mgr = ProfileManager(base_dir=tmp_path)
    mgr.create_profile("Test", AVATAR_COLORS[0])
    return mgr


@pytest.fixture
def channels():
    return [
        Channel(url="http://cnn.com", name="CNN", group="News"),
        Channel(url="http://espn.com", name="ESPN", group="Sports"),
    ]


@pytest.fixture
def widget(manager, qtbot):
    w = ChannelListWidget(manager=manager)
    qtbot.addWidget(w)
    return w


class TestFavoriteToggleSignal:
    def test_favorite_toggled_signal_exists(self, widget):
        assert hasattr(widget, "favorite_toggled")

    def test_toggle_emits_signal_with_url(self, widget, qtbot, channels):
        widget.load_channels(channels)
        channel_item = widget.item(1)  # CNN (after News header)

        with qtbot.waitSignal(widget.favorite_toggled, timeout=1000) as blocker:
            widget.toggle_favorite_for_item(channel_item)

        assert blocker.args[0] == "http://cnn.com"

    def test_toggle_twice_emits_twice(self, widget, qtbot, channels):
        widget.load_channels(channels)
        channel_item = widget.item(1)

        received = []
        widget.favorite_toggled.connect(lambda url: received.append(url))
        widget.toggle_favorite_for_item(channel_item)
        widget.toggle_favorite_for_item(channel_item)

        assert len(received) == 2
        assert all(u == "http://cnn.com" for u in received)


class TestFavoriteReloadWithoutRefetch:
    def test_reload_shows_favorites_group(self, widget, manager, channels):
        widget.load_channels(channels)
        manager.toggle_favorite("http://cnn.com")
        widget.reload_with_profile(manager.active_profile())
        header = widget.item(0)
        assert header is not None
        assert "Favorites" in header.text() or "⭐" in header.text()

    def test_reload_preserves_channels_count(self, widget, manager, channels):
        widget.load_channels(channels)
        manager.toggle_favorite("http://espn.com")
        widget.reload_with_profile(manager.active_profile())
        # Favorites header + ESPN + News header + CNN + Sports header + ESPN = 6
        assert widget.count() == 6
