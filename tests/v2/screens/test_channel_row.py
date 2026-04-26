from __future__ import annotations

import pytest

from src.models.channel import Channel
from src.v2.screens.home_screen import ChannelRow


class TestChannelRow:
    def test_renders_horizontal_scroll_of_cards(self, qtbot):
        channels = [
            Channel(url="http://a.com", name="CNN"),
            Channel(url="http://b.com", name="BBC"),
        ]
        row = ChannelRow("Noticias", channels)
        qtbot.addWidget(row)
        assert row.findChild(type(row._scroll)) is not None
        # cards + stretch = 3
        assert row._container.layout().count() == 3

    def test_title_label_displayed(self, qtbot):
        channels = [Channel(url="http://a.com", name="CNN")]
        row = ChannelRow("Noticias", channels)
        qtbot.addWidget(row)
        assert row._title.text() == "Noticias"
