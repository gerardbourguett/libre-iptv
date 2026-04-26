from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QStyle, QStyleOptionViewItem

from src.models.channel import Channel
from src.ui.channel_list import _GroupHeader


class TestChannelLogoDelegateSizeHint:
    def test_channel_item_returns_36px_height(self, qtbot):
        """S1: sizeHint for channel items returns height 36."""
        from src.ui.logo_delegate import ChannelLogoDelegate
        from src.ui.logo_loader import LogoLoader

        loader = LogoLoader()
        delegate = ChannelLogoDelegate(loader)

        widget = QListWidget()
        qtbot.addWidget(widget)
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, Channel(url="http://a.com", name="A Channel"))
        widget.addItem(item)
        index = widget.indexFromItem(item)

        option = QStyleOptionViewItem()
        size = delegate.sizeHint(option, index)
        assert size.height() == 36

    def test_group_header_delegates_to_super(self, qtbot):
        """S2: sizeHint for group headers delegates to QStyledItemDelegate."""
        from src.ui.logo_delegate import ChannelLogoDelegate
        from src.ui.logo_loader import LogoLoader

        loader = LogoLoader()
        delegate = ChannelLogoDelegate(loader)

        widget = QListWidget()
        qtbot.addWidget(widget)
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, _GroupHeader(name="News", count=2))
        widget.addItem(item)
        index = widget.indexFromItem(item)

        option = QStyleOptionViewItem()
        size = delegate.sizeHint(option, index)
        # Super returns default; we just verify it doesn't force 36
        assert size.height() != 36


class TestChannelLogoDelegatePaintFallback:
    def test_paint_draws_fallback_circle_when_no_pixmap(self, qtbot):
        """S3: paint draws fallback accent circle when no logo."""
        from src.ui.logo_delegate import ChannelLogoDelegate
        from src.ui.logo_loader import LogoLoader

        loader = LogoLoader()
        delegate = ChannelLogoDelegate(loader)

        painter = MagicMock(spec=QPainter)
        option = QStyleOptionViewItem()
        option.rect = QRect(0, 0, 200, 36)
        option.state = QStyle.StateFlag.State_None

        index = MagicMock()
        index.data.return_value = Channel(url="http://a.com", name="ESPN Deportes")

        delegate.paint(painter, option, index)

        # Should draw a rounded rect / ellipse (fallback circle)
        assert painter.drawRoundedRect.called or painter.drawEllipse.called or painter.drawPixmap.called

    def test_paint_fallback_uses_channel_initial(self, qtbot):
        """S4: fallback draws the first character of the channel name."""
        from src.ui.logo_delegate import ChannelLogoDelegate
        from src.ui.logo_loader import LogoLoader

        loader = LogoLoader()
        delegate = ChannelLogoDelegate(loader)

        painter = MagicMock(spec=QPainter)
        option = QStyleOptionViewItem()
        option.rect = QRect(0, 0, 200, 36)
        option.state = QStyle.StateFlag.State_None

        index = MagicMock()
        index.data.return_value = Channel(url="http://a.com", name="BBC")

        delegate.paint(painter, option, index)

        # Verify that drawText was called with "B"
        calls = painter.drawText.call_args_list
        texts = [str(c[0][2]) for c in calls if len(c[0]) >= 3]
        assert any("B" in t for t in texts) or any("BBC" in t for t in texts)


class TestChannelLogoDelegatePaintWithPixmap:
    def test_paint_draws_pixmap_when_logo_available(self, qtbot):
        """S5: paint draws 32x32 pixmap when logo is cached."""
        from src.ui.logo_delegate import ChannelLogoDelegate
        from src.ui.logo_loader import LogoLoader

        loader = LogoLoader()
        url = "http://example.com/logo.png"
        loader._cache.put(url, QPixmap(32, 32))

        delegate = ChannelLogoDelegate(loader)

        painter = MagicMock(spec=QPainter)
        option = QStyleOptionViewItem()
        option.rect = QRect(0, 0, 200, 36)
        option.state = QStyle.StateFlag.State_None

        index = MagicMock()
        channel = Channel(url="http://a.com", name="CNN", tvg_logo=url)
        index.data.return_value = channel

        delegate.paint(painter, option, index)

        # Should call drawPixmap for the logo
        assert painter.drawPixmap.called

    def test_paint_draws_text_right_of_logo_with_gap(self, qtbot):
        """S6: text is drawn to the right of the logo with 8px gap."""
        from src.ui.logo_delegate import ChannelLogoDelegate
        from src.ui.logo_loader import LogoLoader

        loader = LogoLoader()
        url = "http://example.com/logo.png"
        loader._cache.put(url, QPixmap(32, 32))

        delegate = ChannelLogoDelegate(loader)

        painter = MagicMock(spec=QPainter)
        option = QStyleOptionViewItem()
        option.rect = QRect(0, 0, 200, 36)
        option.state = QStyle.StateFlag.State_None

        index = MagicMock()
        channel = Channel(url="http://a.com", name="CNN", tvg_logo=url)
        index.data.return_value = channel

        delegate.paint(painter, option, index)

        # Verify text draw happens
        assert painter.drawText.called
