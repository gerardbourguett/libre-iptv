from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.i18n import init_translator
from src.models.channel import Channel
from src.models.programme import Programme
from src.ui.main_window import MainWindow


@pytest.fixture(autouse=True)
def translator(qapp):
    init_translator(locales_dir=None)


@pytest.fixture(autouse=True)
def reset_vlc_manager():
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


@pytest.fixture
def window(qtbot, mock_vlc):
    w = MainWindow()
    qtbot.addWidget(w)
    return w


class TestMainWindowEpgStatusBar:
    def test_status_bar_shows_programme_when_epg_present(self, window):
        ch = Channel(url="http://bbc.com", name="BBC", tvg_id="bbc1")
        window._epg_service._programmes = {
            "bbc1": [
                Programme(
                    channel="bbc1",
                    title="News",
                    start="20260425143000 +0000",
                    stop="20260425150000 +0000",
                )
            ]
        }
        window._channels = [ch]
        window._on_channel_selected(ch)
        msg = window.statusBar().currentMessage()
        assert "BBC" in msg
        assert "News" in msg
        assert "20260425143000" in msg

    def test_status_bar_shows_only_channel_name_when_no_epg(self, window):
        ch = Channel(url="http://bbc.com", name="BBC", tvg_id="bbc1")
        window._epg_service._programmes = {}
        window._channels = [ch]
        window._on_channel_selected(ch)
        assert window.statusBar().currentMessage() == "BBC"

    def test_status_bar_shows_only_channel_name_when_no_tvg_id(self, window):
        ch = Channel(url="http://bbc.com", name="BBC", tvg_id="")
        window._epg_service._programmes = {
            "": [
                Programme(
                    channel="",
                    title="News",
                    start="20260425143000 +0000",
                    stop="20260425150000 +0000",
                )
            ]
        }
        window._channels = [ch]
        window._on_channel_selected(ch)
        assert window.statusBar().currentMessage() == "BBC"
