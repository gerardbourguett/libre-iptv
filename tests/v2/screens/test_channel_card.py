from __future__ import annotations

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel

from src.models.channel import Channel
from src.v2.screens.home_screen import ChannelCard


class TestChannelCard:
    def test_displays_channel_name(self, qtbot):
        ch = Channel(url="http://a.com", name="CNN")
        card = ChannelCard(ch)
        qtbot.addWidget(card)
        assert "CNN" in card.layout().itemAt(1).widget().text()

    def test_emits_clicked_with_channel(self, qtbot):
        from PyQt6.QtCore import QPointF, Qt
        from PyQt6.QtGui import QMouseEvent
        ch = Channel(url="http://a.com", name="CNN")
        card = ChannelCard(ch)
        qtbot.addWidget(card)
        with qtbot.waitSignal(card.clicked, timeout=1000) as blocker:
            event = QMouseEvent(
                QMouseEvent.Type.MouseButtonPress,
                QPointF(0, 0),
                QPointF(0, 0),
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.LeftButton,
                Qt.KeyboardModifier.NoModifier,
            )
            card.mousePressEvent(event)
        assert blocker.args[0] is ch

    def test_channel_stored_as_property(self, qtbot):
        ch = Channel(url="http://a.com", name="CNN")
        card = ChannelCard(ch)
        qtbot.addWidget(card)
        assert card.channel is ch
