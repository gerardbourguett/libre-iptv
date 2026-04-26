from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PyQt6.QtCore import QEvent, QObject, Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.models.channel import Channel
from src.ui.player_widget import PlayerWidget

if TYPE_CHECKING:
    from src.services.epg_service import EpgService


class _LiveChannelList(QListWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(
            "QListWidget { border: none; background: #161616; outline: none; }"
            "QListWidget::item { padding: 8px 12px; color: #e0e0e0; min-height: 24px; }"
            "QListWidget::item:selected { background: #00bcd4; color: #000000; }"
            "QListWidget::item:hover:!selected { background: #222222; }"
        )


class LiveTvScreen(QWidget):
    channel_selected = pyqtSignal(object)  # Channel

    def __init__(
        self,
        channels: list[Channel] | None = None,
        epg_service: EpgService | None = None,
        epg_data: dict[str, dict[str, Any]] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._channels: list[Channel] = list(channels) if channels else []
        self._epg_service = epg_service
        self._epg_data = epg_data or {}
        self._current_index = -1

        self._channel_list = _LiveChannelList(self)
        self._player = PlayerWidget(self)
        self._player.setMinimumWidth(200)

        self._search = QLineEdit(self)
        self._search.setPlaceholderText("Buscar canal...")
        self._search.setStyleSheet(
            "QLineEdit { background: #1e1e1e; color: #e0e0e0; "
            "border: 1px solid #2a2a2a; border-radius: 6px; padding: 6px 10px; }"
            "QLineEdit:focus { border-color: #00bcd4; }"
        )

        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(0)
        left.addWidget(self._search)
        left.addWidget(self._channel_list)

        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        hbox.addLayout(left, 7)
        hbox.addWidget(self._player, 3)

        self._channel_list.itemClicked.connect(self._on_item_clicked)
        self._search.textChanged.connect(self._filter_channels)

        # Install event filter on search to catch Esc when it has focus
        self._search.installEventFilter(self)

        if self._channels:
            self.load_channels(self._channels)

    def load_channels(
        self,
        channels: list[Channel],
        epg_data: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        self._channels = list(channels)
        if epg_data is not None:
            self._epg_data = epg_data
        self._channel_list.clear()
        for ch in self._channels:
            item = self._make_item(ch)
            self._channel_list.addItem(item)
        if self._channels:
            self._select_channel(0)

    def _make_item(self, ch: Channel) -> QListWidgetItem:
        epg = self._epg_data.get(ch.tvg_id) if ch.tvg_id else None
        if epg and epg.get("now_title"):
            start = epg.get("start", "")
            end = epg.get("end", "")
            text = (
                f"{ch.name}\n▶ {epg['now_title']}  "
                f"({start}–{end})"
            )
        else:
            text = f"{ch.name}\nSin información"
        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, ch)
        return item

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        ch = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(ch, Channel):
            self._current_index = self._channels.index(ch)
            self.channel_selected.emit(ch)
            self._play_channel(ch)

    def _select_channel(self, index: int) -> None:
        if not self._channels:
            return
        self._current_index = index % len(self._channels)
        self._channel_list.setCurrentRow(self._current_index)
        ch = self._channels[self._current_index]
        self.channel_selected.emit(ch)
        self._play_channel(ch)

    def play_channel(self, ch: Channel) -> None:
        self._play_channel(ch)

    def _play_channel(self, ch: Channel) -> None:
        self._player.play(ch.url)

    def _handle_key(self, key: Qt.Key) -> None:
        if not self._channels:
            return
        if key == Qt.Key.Key_Down:
            new_index = self._current_index + 1
            if new_index >= len(self._channels):
                new_index = 0
            self._select_channel(new_index)
        elif key == Qt.Key.Key_Up:
            new_index = self._current_index - 1
            if new_index < 0:
                new_index = len(self._channels) - 1
            self._select_channel(new_index)

    def keyPressEvent(self, event: QKeyEvent | None) -> None:
        if event is None:
            super().keyPressEvent(event)
            return
        key = event.key()
        if key == Qt.Key.Key_Escape:
            if self._search.hasFocus() and self._search.text():
                self._search.clear()
                event.accept()
                return
        elif key in (Qt.Key.Key_Down, Qt.Key.Key_Up):
            self._handle_key(Qt.Key(key))
            event.accept()
            return
        super().keyPressEvent(event)

    def _filter_channels(self, text: str) -> None:
        q = text.lower().strip()
        for i in range(self._channel_list.count()):
            item = self._channel_list.item(i)
            if item is None:
                continue
            ch = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(ch, Channel):
                item.setHidden(q not in ch.name.lower())

    def eventFilter(self, obj: QObject | None, event: QEvent | None) -> bool:
        """Catch Esc key on search field when it has focus."""
        if obj is self._search and isinstance(event, QKeyEvent):
            if event.key() == Qt.Key.Key_Escape:
                self._on_search_esc()
                event.accept()
                return True
        return super().eventFilter(obj, event)

    def _on_search_esc(self) -> None:
        self._search.clear()
