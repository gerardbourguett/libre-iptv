from __future__ import annotations

import pytest

from src.models.channel import Channel
from src.v2.screens.epg_screen import EpgScreen


def _ch(name: str, tvg_id: str = "") -> Channel:
    return Channel(url=f"http://example.com/{name}", name=name, tvg_id=tvg_id)


class TestEpgScreenCreation:
    def test_creates_without_channels(self, qtbot) -> None:
        screen = EpgScreen()
        qtbot.addWidget(screen)
        assert screen is not None

    def test_creates_with_channels(self, qtbot) -> None:
        screen = EpgScreen(channels=[_ch("CNN"), _ch("BBC")])
        qtbot.addWidget(screen)
        assert screen is not None


class TestEpgChannelList:
    def test_channel_count_matches(self, qtbot) -> None:
        screen = EpgScreen(channels=[_ch("CNN"), _ch("BBC"), _ch("ESPN")])
        qtbot.addWidget(screen)
        assert screen.channel_count() == 3

    def test_empty_by_default(self, qtbot) -> None:
        screen = EpgScreen()
        qtbot.addWidget(screen)
        assert screen.channel_count() == 0

    def test_load_channels_updates_list(self, qtbot) -> None:
        screen = EpgScreen()
        qtbot.addWidget(screen)
        screen.load_channels([_ch("RCN"), _ch("Caracol")])
        assert screen.channel_count() == 2

    def test_load_channels_replaces_previous(self, qtbot) -> None:
        screen = EpgScreen(channels=[_ch("CNN")])
        qtbot.addWidget(screen)
        screen.load_channels([_ch("A"), _ch("B"), _ch("C")])
        assert screen.channel_count() == 3


class TestEpgChannelSelected:
    def test_channel_selected_signal_on_click(self, qtbot) -> None:
        channels = [_ch("CNN"), _ch("BBC")]
        screen = EpgScreen(channels=channels)
        qtbot.addWidget(screen)
        received: list[Channel] = []
        screen.channel_selected.connect(received.append)
        screen._channel_list.itemClicked.emit(screen._channel_list.item(0))
        assert len(received) == 1
        assert received[0].name == "CNN"

    def test_info_panel_updated_on_select(self, qtbot) -> None:
        screen = EpgScreen(channels=[_ch("Test Channel")])
        qtbot.addWidget(screen)
        screen._channel_list.itemClicked.emit(screen._channel_list.item(0))
        assert "Test Channel" in screen._info_title.text()


class TestEpgInfoPanel:
    def test_info_panel_widgets_exist(self, qtbot) -> None:
        screen = EpgScreen()
        qtbot.addWidget(screen)
        assert screen._info_title is not None
        assert screen._info_now is not None
