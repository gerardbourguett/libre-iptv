from __future__ import annotations

import pytest

from src.models.channel import Channel
from src.v2.screens.home_screen import ChannelRow


class TestEmptyRowHidden:
    def test_row_with_zero_channels_is_hidden(self, qtbot):
        row = ChannelRow("Deportes", [])
        qtbot.addWidget(row)
        assert row.isHidden()

    def test_row_with_channels_is_visible(self, qtbot):
        channels = [Channel(url="http://a.com", name="ESPN")]
        row = ChannelRow("Deportes", channels)
        qtbot.addWidget(row)
        assert row.isVisible()
