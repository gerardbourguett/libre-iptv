from __future__ import annotations

import pytest

from src.models.channel import Channel
from src.v2.screens.vod_screen import VodScreen


def _ch(name: str, group: str, *, is_vod: bool = False, is_series: bool = False) -> Channel:
    return Channel(
        url=f"http://example.com/{name}",
        name=name,
        group=group,
        is_live=not (is_vod or is_series),
        is_vod=is_vod,
        is_series=is_series,
    )


class TestVodScreenCreation:
    def test_creates_without_channels(self, qtbot) -> None:
        screen = VodScreen()
        qtbot.addWidget(screen)
        assert screen is not None

    def test_creates_with_channels(self, qtbot) -> None:
        channels = [_ch("Movie A", "Películas", is_vod=True)]
        screen = VodScreen(channels=channels)
        qtbot.addWidget(screen)
        assert screen is not None


class TestVodChannelSeparation:
    def test_vod_channels(self, qtbot) -> None:
        channels = [
            _ch("Movie A", "Películas", is_vod=True),
            _ch("Movie B", "Películas", is_vod=True),
            _ch("Live TV", "General"),
        ]
        screen = VodScreen(channels=channels)
        qtbot.addWidget(screen)
        assert len(screen.vod_channels()) == 2

    def test_series_channels(self, qtbot) -> None:
        channels = [
            _ch("Breaking Bad", "Series", is_series=True),
            _ch("Movie A", "Películas", is_vod=True),
        ]
        screen = VodScreen(channels=channels)
        qtbot.addWidget(screen)
        assert len(screen.series_channels()) == 1

    def test_live_not_included_in_vod(self, qtbot) -> None:
        channels = [
            _ch("Live News", "Noticias"),
            _ch("Movie A", "Películas", is_vod=True),
        ]
        screen = VodScreen(channels=channels)
        qtbot.addWidget(screen)
        assert all(ch.is_vod for ch in screen.vod_channels())

    def test_empty_list(self, qtbot) -> None:
        screen = VodScreen(channels=[])
        qtbot.addWidget(screen)
        assert screen.vod_channels() == []
        assert screen.series_channels() == []


class TestVodLoadChannels:
    def test_load_channels_updates_state(self, qtbot) -> None:
        screen = VodScreen()
        qtbot.addWidget(screen)
        channels = [_ch("Film X", "Cine", is_vod=True)]
        screen.load_channels(channels)
        assert len(screen.vod_channels()) == 1

    def test_load_replaces_previous(self, qtbot) -> None:
        old = [_ch("Old Movie", "Películas", is_vod=True)]
        screen = VodScreen(channels=old)
        qtbot.addWidget(screen)
        new = [
            _ch("New A", "Acción", is_vod=True),
            _ch("New B", "Drama", is_vod=True),
        ]
        screen.load_channels(new)
        assert len(screen.vod_channels()) == 2


class TestVodChannelSelected:
    def test_channel_selected_signal(self, qtbot) -> None:
        channels = [_ch("Movie A", "Películas", is_vod=True)]
        screen = VodScreen(channels=channels)
        qtbot.addWidget(screen)
        received: list[Channel] = []
        screen.channel_selected.connect(received.append)
        screen._rows[0].channel_selected.emit(channels[0])
        assert len(received) == 1
        assert received[0].name == "Movie A"

    def test_groups_separated_by_group_title(self, qtbot) -> None:
        channels = [
            _ch("Action Movie", "Acción", is_vod=True),
            _ch("Drama Film", "Drama", is_vod=True),
        ]
        screen = VodScreen(channels=channels)
        qtbot.addWidget(screen)
        row_titles = [r._title for r in screen._rows]
        assert "Acción" in row_titles
        assert "Drama" in row_titles
