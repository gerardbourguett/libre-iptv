from __future__ import annotations

import pytest
from PyQt6.QtCore import Qt

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


class TestZapping:
    def test_down_wraps_to_first(self, qtbot):
        channels = [
            Channel(url="http://a.com", name="Ch1"),
            Channel(url="http://b.com", name="Ch2"),
            Channel(url="http://c.com", name="Ch3"),
        ]
        screen = LiveTvScreen(channels)
        qtbot.addWidget(screen)
        screen._select_channel(1)  # Ch2
        assert screen._current_index == 1
        screen._handle_key(Qt.Key.Key_Down)
        assert screen._current_index == 2
        screen._handle_key(Qt.Key.Key_Down)
        assert screen._current_index == 0  # wrap

    def test_up_wraps_to_last(self, qtbot):
        channels = [
            Channel(url="http://a.com", name="Ch1"),
            Channel(url="http://b.com", name="Ch2"),
            Channel(url="http://c.com", name="Ch3"),
        ]
        screen = LiveTvScreen(channels)
        qtbot.addWidget(screen)
        screen._select_channel(0)
        screen._handle_key(Qt.Key.Key_Up)
        assert screen._current_index == 2  # wrap to last

    def test_highlight_moves(self, qtbot):
        channels = [
            Channel(url="http://a.com", name="Ch1"),
            Channel(url="http://b.com", name="Ch2"),
        ]
        screen = LiveTvScreen(channels)
        qtbot.addWidget(screen)
        screen._select_channel(0)
        assert screen._current_index == 0
        screen._handle_key(Qt.Key.Key_Down)
        assert screen._current_index == 1

    def test_channel_selected_signal_emitted(self, qtbot):
        channels = [
            Channel(url="http://a.com", name="Ch1"),
            Channel(url="http://b.com", name="Ch2"),
        ]
        screen = LiveTvScreen(channels)
        qtbot.addWidget(screen)
        with qtbot.waitSignal(screen.channel_selected, timeout=1000) as blocker:
            screen._select_channel(1)
        assert blocker.args[0].name == "Ch2"
