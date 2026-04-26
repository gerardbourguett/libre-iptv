from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt6.QtWidgets import QStyle, QStyledItemDelegate, QStyleOptionViewItem

from src.i18n import t
from src.models.channel import Channel
from src.ui.logo_loader import LogoLoader

if TYPE_CHECKING:
    from PyQt6.QtCore import QModelIndex
    from PyQt6.QtWidgets import QWidget


class ChannelLogoDelegate(QStyledItemDelegate):
    def __init__(
        self,
        logo_loader: LogoLoader,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._logo_loader = logo_loader

    def sizeHint(
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ) -> QSize:
        data = index.data(Qt.ItemDataRole.UserRole)
        if isinstance(data, Channel):
            epg = index.data(Qt.ItemDataRole.UserRole + 1)
            if epg is not None and (epg.now_title or epg.next_title):
                return QSize(0, 56)
            return QSize(0, 36)
        return super().sizeHint(option, index)

    def paint(
        self,
        painter: QPainter | None,
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ) -> None:
        from src.ui.channel_list import _EpgInfo, _GroupHeader

        data = index.data(Qt.ItemDataRole.UserRole)
        if isinstance(data, _GroupHeader):
            super().paint(painter, option, index)
            return

        if not isinstance(data, Channel):
            super().paint(painter, option, index)
            return

        channel: Channel = data
        epg_data = index.data(Qt.ItemDataRole.UserRole + 1)
        epg: _EpgInfo | None = epg_data if isinstance(epg_data, _EpgInfo) else None

        if painter is None:
            return

        painter.save()

        # Draw selection background if selected
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        elif option.state & QStyle.StateFlag.State_MouseOver:
            painter.fillRect(option.rect, QColor("#222222"))

        logo_size = 32
        gap = 8
        margin_left = 12
        has_epg = epg is not None and (epg.now_title or epg.next_title)
        margin_top = (option.rect.height() - logo_size) // 2 if not has_epg else 4

        logo_rect = QRect(
            option.rect.x() + margin_left,
            option.rect.y() + margin_top,
            logo_size,
            logo_size,
        )

        pixmap: QPixmap | None = None
        if channel.tvg_logo:
            pixmap = self._logo_loader.get_pixmap(channel.tvg_logo)
            if (
                pixmap is not None
                and not pixmap.isNull()
                and pixmap is not LogoLoader._FAILED
            ):
                # Draw rounded pixmap
                path = painter.clipPath()
                painter.setClipRect(logo_rect)
                painter.drawPixmap(logo_rect, pixmap)
                painter.setClipPath(path)
            else:
                pixmap = None

        if pixmap is None:
            # Draw fallback circle
            painter.setBrush(QColor("#00bcd4"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(logo_rect)

            # Draw initial
            initial = channel.name[0].upper() if channel.name else "?"
            painter.setPen(QColor("#ffffff"))
            font = QFont()
            font.setBold(True)
            font.setPointSize(12)
            painter.setFont(font)
            painter.drawText(logo_rect, Qt.AlignmentFlag.AlignCenter, initial)

        # Draw channel name text
        text_x = logo_rect.right() + gap
        text_w = option.rect.width() - text_x - margin_left
        painter.setPen(
            QColor("#000000")
            if option.state & QStyle.StateFlag.State_Selected
            else QColor("#e0e0e0")
        )
        font = QFont()
        font.setPointSize(13)
        painter.setFont(font)

        if has_epg:
            assert epg is not None
            name_rect = QRect(text_x, option.rect.y() + 2, text_w, 18)
            painter.drawText(
                name_rect,
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                channel.name,
            )
            line_y = name_rect.bottom()
            font_small = QFont()
            font_small.setPointSize(10)
            painter.setFont(font_small)
            if epg.now_title:
                now_rect = QRect(text_x, line_y, text_w, 16)
                painter.setPen(
                    QColor("#000000")
                    if option.state & QStyle.StateFlag.State_Selected
                    else QColor("#4caf50")
                )
                painter.drawText(
                    now_rect,
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                    f"▶ {epg.now_title}",
                )
                line_y = now_rect.bottom()
            if epg.next_title:
                next_rect = QRect(text_x, line_y, text_w, 16)
                painter.setPen(
                    QColor("#000000")
                    if option.state & QStyle.StateFlag.State_Selected
                    else QColor("#9e9e9e")
                )
                painter.drawText(
                    next_rect,
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                    f"{t('channel_list.next')} {epg.next_title}",
                )
        else:
            text_rect = QRect(text_x, option.rect.y(), text_w, option.rect.height())
            painter.drawText(
                text_rect,
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                channel.name,
            )

        painter.restore()
