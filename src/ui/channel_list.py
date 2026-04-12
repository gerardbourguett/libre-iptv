from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.models.channel import Channel

_UNCATEGORIZED = "Uncategorized"


class ChannelListWidget(QListWidget):
    channel_selected = pyqtSignal(Channel)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.itemClicked.connect(self._on_item_clicked)

    def load_channels(self, channels: list[Channel]) -> None:
        self.clear()
        groups: dict[str, list[Channel]] = {}
        for ch in channels:
            key = ch.group if ch.group else _UNCATEGORIZED
            groups.setdefault(key, []).append(ch)

        for group_name, group_channels in groups.items():
            self._add_header(group_name)
            for ch in group_channels:
                self._add_channel(ch)

    def _add_header(self, text: str) -> None:
        item = QListWidgetItem(text)
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        font = QFont()
        font.setBold(True)
        item.setFont(font)
        self.addItem(item)

    def _add_channel(self, channel: Channel) -> None:
        item = QListWidgetItem(channel.name)
        item.setData(Qt.ItemDataRole.UserRole, channel)
        self.addItem(item)

    def filter_channels(self, text: str) -> None:
        query = text.lower().strip()
        # Track which header indices have at least one visible channel
        header_has_visible: dict[int, bool] = {}
        current_header_idx: int | None = None

        for i in range(self.count()):
            item = self.item(i)
            assert item is not None
            channel = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(channel, Channel):
                # Channel item: show if query is empty or name matches
                visible = not query or query in channel.name.lower()
                item.setHidden(not visible)
                if current_header_idx is not None and visible:
                    header_has_visible[current_header_idx] = True
            else:
                # Header item
                current_header_idx = i
                header_has_visible[i] = False

        # Second pass: hide headers with no visible channels
        for header_idx, has_visible in header_has_visible.items():
            hdr = self.item(header_idx)
            assert hdr is not None
            hdr.setHidden(not has_visible)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        channel = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(channel, Channel):
            self.channel_selected.emit(channel)


class ChannelListPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search channels\u2026")
        self.channel_list = ChannelListWidget()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._search)
        layout.addWidget(self.channel_list)

        self._search.textChanged.connect(self.channel_list.filter_channels)

        # Expose signal for external wiring convenience
        self.channel_selected = self.channel_list.channel_selected
