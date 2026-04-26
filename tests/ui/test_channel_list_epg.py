from __future__ import annotations

from typing import Any

import pytest

from src.i18n import init_translator
from src.models.channel import Channel
from src.ui.channel_list import ChannelListWidget, _EpgInfo


@pytest.fixture(autouse=True)
def translator(qapp: Any) -> None:
    init_translator(locales_dir=None)


class TestChannelListEpg:
    def test_channel_shows_now_next_when_epg_present(self, qtbot: Any) -> None:
        widget = ChannelListWidget()
        qtbot.addWidget(widget)
        channels = [Channel(url="http://ch1.com", name="Ch1", tvg_id="ch1")]
        epg_data = {"ch1": _EpgInfo(now_title="News", next_title="Sports")}
        widget.load_channels(channels, epg_data=epg_data)
        item = widget.item(1)  # 0 is header, 1 is channel
        assert item is not None
        text = item.text()
        from src.i18n import t
        assert "▶ News" in text
        assert f"{t('channel_list.next')} Sports" in text

    def test_channel_shows_nothing_when_no_epg_match(self, qtbot: Any) -> None:
        widget = ChannelListWidget()
        qtbot.addWidget(widget)
        channels = [Channel(url="http://ch1.com", name="Ch1", tvg_id="ch1")]
        epg_data: dict[str, _EpgInfo] = {}
        widget.load_channels(channels, epg_data=epg_data)
        item = widget.item(1)
        assert item is not None
        assert item.text() == "Ch1"

    def test_channel_shows_only_now_when_no_next(self, qtbot: Any) -> None:
        widget = ChannelListWidget()
        qtbot.addWidget(widget)
        channels = [Channel(url="http://ch1.com", name="Ch1", tvg_id="ch1")]
        epg_data = {"ch1": _EpgInfo(now_title="News", next_title="")}
        widget.load_channels(channels, epg_data=epg_data)
        item = widget.item(1)
        assert item is not None
        text = item.text()
        from src.i18n import t
        assert "▶ News" in text
        assert t("channel_list.next") not in text
