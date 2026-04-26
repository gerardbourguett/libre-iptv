from __future__ import annotations

import pytest

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


class TestEpgSublabel:
    def test_shows_programme_when_epg_present(self, qtbot):
        channels = [Channel(url="http://a.com", name="CNN", tvg_id="cnn")]
        epg_data = {"cnn": {"now_title": "Noticias 12", "start": "12:00", "end": "13:00"}}
        screen = LiveTvScreen(channels, epg_data=epg_data)
        qtbot.addWidget(screen)
        item = screen._channel_list.item(0)
        assert "Noticias 12" in item.text()

    def test_shows_sin_informacion_when_no_epg(self, qtbot):
        channels = [Channel(url="http://a.com", name="CNN", tvg_id="cnn")]
        screen = LiveTvScreen(channels, epg_data={})
        qtbot.addWidget(screen)
        item = screen._channel_list.item(0)
        assert "Sin información" in item.text()

    def test_epg_info_passed_to_list_widget(self, qtbot):
        channels = [Channel(url="http://a.com", name="CNN", tvg_id="cnn")]
        epg_data = {"cnn": {"now_title": "Breaking", "start": "10:00", "end": "11:00"}}
        screen = LiveTvScreen(channels, epg_data=epg_data)
        qtbot.addWidget(screen)
        item = screen._channel_list.item(0)
        assert "Breaking" in item.text()
