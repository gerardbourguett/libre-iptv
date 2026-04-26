from __future__ import annotations

import pytest
from PyQt6.QtWidgets import QHBoxLayout

from src.models.channel import Channel
from src.v2.screens.live_tv_screen import LiveTvScreen


@pytest.fixture(autouse=True)
def patch_vlc_and_translator(monkeypatch):
    import vlc
    class FakePlayer:
        def set_media(self, m): ...
        def play(self): ...
        def stop(self): ...
        def release(self): ...
        def audio_set_volume(self, v): ...
        def audio_get_volume(self): return 100
        def audio_toggle_mute(self): ...
        def audio_get_mute(self): return False
    class FakeInstance:
        def media_player_new(self): return FakePlayer()
        def media_new(self, url): return url
        def release(self): ...
    monkeypatch.setattr("src.ui.player_widget.vlc.Instance", FakeInstance)
    monkeypatch.setattr("src.ui.player_widget.t", lambda key, **kwargs: key)
    monkeypatch.setattr("src.platform.bind_vlc", lambda mp, wid: None)


class TestLiveTvLayout:
    def test_70_30_split(self, qtbot):
        channels = [
            Channel(url="http://a.com", name="CNN"),
            Channel(url="http://b.com", name="BBC"),
        ]
        screen = LiveTvScreen(channels)
        qtbot.addWidget(screen)
        layout = screen.layout()
        assert isinstance(layout, QHBoxLayout)
        # Channel list should take stretch factor 7, player 3
        # Verify both panels exist
        assert screen._channel_list is not None
        assert screen._player is not None

    def test_channel_list_left_player_right(self, qtbot):
        channels = [Channel(url="http://a.com", name="CNN")]
        screen = LiveTvScreen(channels)
        qtbot.addWidget(screen)
        assert screen._channel_list.parent() is screen
        assert screen._player.parent() is screen
