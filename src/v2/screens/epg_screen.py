from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from src.models.channel import Channel

if TYPE_CHECKING:
    from src.services.epg_service import EpgService

_BG = "#060810"
_SURFACE = "#0c0e18"
_ELEVATED = "#121522"
_BORDER = "rgba(255,255,255,0.06)"
_TEXT = "#e8eaf0"
_DIM = "#555761"
_SEC = "#9698a0"
_ACCENT = "#001999"


class EpgScreen(QWidget):
    channel_selected = pyqtSignal(object)  # Channel

    def __init__(
        self,
        channels: list[Channel] | None = None,
        epg_service: EpgService | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._channels: list[Channel] = list(channels) if channels else []
        self._epg_service = epg_service

        self.setStyleSheet(f"background: {_BG};")

        # Header
        header = QWidget()
        header.setFixedHeight(56)
        header.setStyleSheet(
            f"background: {_SURFACE}; border-bottom: 1px solid {_BORDER};"
        )
        header_row = QHBoxLayout(header)
        header_row.setContentsMargins(24, 0, 24, 0)
        header_row.setSpacing(12)
        h_lbl = QLabel("TV GUIDE")
        h_lbl.setStyleSheet(
            f"color: {_TEXT}; font-size: 16px; font-weight: 700;"
            "letter-spacing: -0.01em; background: transparent; border: none;"
        )
        header_row.addWidget(h_lbl)
        header_row.addStretch()

        # Channel list (left pane)
        self._channel_list = QListWidget()
        self._channel_list.setFixedWidth(240)
        self._channel_list.setStyleSheet(
            f"QListWidget {{"
            f"  border: none; background: {_SURFACE}; outline: none;"
            f"  border-right: 1px solid {_BORDER};"
            f"}}"
            f"QListWidget::item {{"
            f"  padding: 10px 14px; color: {_TEXT}; min-height: 28px;"
            f"  border-bottom: 1px solid {_BORDER};"
            f"}}"
            f"QListWidget::item:selected {{"
            f"  background: rgba(0,25,153,0.15); color: {_TEXT};"
            f"  border-left: 2px solid {_ACCENT};"
            f"}}"
            f"QListWidget::item:hover:!selected {{"
            f"  background: rgba(255,255,255,0.03);"
            f"}}"
        )

        # Info panel (right pane)
        self._info_panel = QWidget()
        self._info_panel.setStyleSheet(f"background: {_BG};")
        info_layout = QVBoxLayout(self._info_panel)
        info_layout.setContentsMargins(24, 24, 24, 24)
        info_layout.setSpacing(12)

        tag = QLabel("GUÍA EPG")
        tag.setStyleSheet(
            f"color: {_DIM}; font-size: 9px; font-weight: 700;"
            "letter-spacing: 0.15em; background: transparent; border: none;"
        )
        info_layout.addWidget(tag)

        self._info_title = QLabel("Seleccioná un canal")
        self._info_title.setStyleSheet(
            f"color: {_TEXT}; font-size: 18px; font-weight: 700;"
            "background: transparent; border: none;"
        )
        self._info_title.setWordWrap(True)
        info_layout.addWidget(self._info_title)

        self._info_now = QLabel("")
        self._info_now.setStyleSheet(
            f"color: {_ACCENT}; font-size: 13px; font-weight: 600;"
            "background: transparent; border: none;"
        )
        self._info_now.setWordWrap(True)
        info_layout.addWidget(self._info_now)

        self._info_desc = QLabel("")
        self._info_desc.setStyleSheet(
            f"color: {_SEC}; font-size: 12px; background: transparent; border: none;"
        )
        self._info_desc.setWordWrap(True)
        info_layout.addWidget(self._info_desc)

        info_layout.addStretch()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(
            f"QSplitter::handle {{ background: {_BORDER}; width: 1px; }}"
        )
        splitter.addWidget(self._channel_list)
        splitter.addWidget(self._info_panel)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        main.addWidget(header)
        main.addWidget(splitter)

        self._channel_list.itemClicked.connect(self._on_channel_clicked)

        if self._channels:
            self._populate()

    def load_channels(
        self,
        channels: list[Channel],
        epg_service: EpgService | None = None,
    ) -> None:
        self._channels = list(channels)
        if epg_service is not None:
            self._epg_service = epg_service
        self._populate()

    def _populate(self) -> None:
        self._channel_list.clear()
        for ch in self._channels:
            text = ch.name
            if self._epg_service and ch.tvg_id:
                now, _ = self._epg_service.get_now_next(ch.tvg_id)
                if now:
                    text = f"{ch.name}\n▶ {now.title}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, ch)
            self._channel_list.addItem(item)

    def _on_channel_clicked(self, item: QListWidgetItem) -> None:
        ch = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(ch, Channel):
            return
        self.channel_selected.emit(ch)
        self._update_info(ch)

    def _update_info(self, ch: Channel) -> None:
        self._info_title.setText(ch.name)
        if self._epg_service and ch.tvg_id:
            now, _ = self._epg_service.get_now_next(ch.tvg_id)
            if now:
                self._info_now.setText(f"▶ {now.title}")
                self._info_desc.setText(now.description)
                return
        self._info_now.setText("Sin información de programación")
        self._info_desc.setText("")

    def channel_count(self) -> int:
        return self._channel_list.count()
