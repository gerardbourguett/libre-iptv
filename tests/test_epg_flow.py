from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.i18n import init_translator
from src.models.channel import Channel
from src.models.programme import EpgChannel, Programme
from src.profiles.manager import ProfileManager
from src.ui.main_window import MainWindow


@pytest.fixture(autouse=True)
def translator(qapp: Any) -> None:
    init_translator(locales_dir=None)


@pytest.fixture(autouse=True)
def reset_vlc_manager() -> None:
    from src.core.vlc_manager import VlcManager
    VlcManager._instance = None
    yield


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


class TestEpgFlow:
    def test_profile_switch_triggers_epg_fetch_and_channel_list_shows_now_next(
        self, qtbot: Any, tmp_path: Path, mock_vlc
    ) -> None:
        mgr = ProfileManager(base_dir=tmp_path)
        profile = mgr.create_profile("Test", "#00bcd4")
        mgr.update_epg_url(profile.id, "https://example.com/epg.xml")
        mgr.save_active()

        window = MainWindow(manager=mgr)
        qtbot.addWidget(window)

        channels = [
            Channel(url="http://ch1.com", name="Ch1", tvg_id="ch1", group="News"),
        ]
        window._channels = channels

        with patch("src.services.epg_service.parse_xmltv_url") as mock_fetch, patch(
            "src.services.epg_service.time.strftime",
            lambda fmt, gm: "20260101003000 +0000" if fmt == "%Y%m%d%H%M%S %z" else "",
        ):
            mock_fetch.return_value = (
                [EpgChannel(id="ch1", names=["Ch1"])],
                [
                    Programme(
                        channel="ch1",
                        title="News",
                        start="20260101000000 +0000",
                        stop="20260101010000 +0000",
                    ),
                    Programme(
                        channel="ch1",
                        title="Sports",
                        start="20260101010000 +0000",
                        stop="20260101020000 +0000",
                    ),
                ],
            )
            with qtbot.waitSignal(window._epg_service.epg_ready, timeout=2000):
                window._epg_service.start("https://example.com/epg.xml")

            window._reload_channel_list()
            item = window._channel_list.item(1)  # header at 0, channel at 1
            assert item is not None
            text = item.text()
            from src.i18n import t
            assert "▶ News" in text
            assert f"{t('channel_list.next')} Sports" in text

    def test_no_epg_url_silent_fallback(
        self, qtbot: Any, tmp_path: Path, mock_vlc
    ) -> None:
        mgr = ProfileManager(base_dir=tmp_path)
        mgr.create_profile("Test", "#00bcd4")
        mgr.save_active()

        window = MainWindow(manager=mgr)
        qtbot.addWidget(window)

        channels = [
            Channel(url="http://ch1.com", name="Ch1", tvg_id="ch1", group="News"),
        ]
        window._channels = channels
        window._reload_channel_list()

        item = window._channel_list.item(1)
        assert item is not None
        assert item.text() == "Ch1"
        assert "▶" not in item.text()
