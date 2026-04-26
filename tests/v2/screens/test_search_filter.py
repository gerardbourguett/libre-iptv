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


class TestSearchFilter:
    def test_typing_filters_by_name(self, qtbot):
        channels = [
            Channel(url="http://a.com", name="CNN"),
            Channel(url="http://b.com", name="BBC"),
            Channel(url="http://c.com", name="ESPN"),
        ]
        screen = LiveTvScreen(channels)
        qtbot.addWidget(screen)
        screen._search.setText("esp")
        # ESPN should be visible, others hidden
        for i in range(screen._channel_list.count()):
            item = screen._channel_list.item(i)
            if item is not None and "ESPN" in item.text():
                assert not item.isHidden()
            elif item is not None and item.flags() & Qt.ItemFlag.ItemIsSelectable:
                assert item.isHidden()

    def test_filter_case_insensitive(self, qtbot):
        channels = [
            Channel(url="http://a.com", name="CNN"),
        ]
        screen = LiveTvScreen(channels)
        qtbot.addWidget(screen)
        screen._search.setText("cnn")
        cnn_item = screen._channel_list.item(0)
        assert not cnn_item.isHidden()

    def test_esc_clears_filter(self, qtbot):
        channels = [
            Channel(url="http://a.com", name="CNN"),
            Channel(url="http://b.com", name="BBC"),
        ]
        screen = LiveTvScreen(channels)
        qtbot.addWidget(screen)
        screen._search.setText("cnn")
        screen._on_search_esc()
        assert screen._search.text() == ""
