from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QVBoxLayout,
    QWidget,
)

from src.models.channel import Channel

if TYPE_CHECKING:
    from src.models.profile import Profile
    from src.profiles.manager import ProfileManager

_UNCATEGORIZED = "Uncategorized"


@dataclass
class _GroupHeader:
    name: str
    count: int
    pinned: bool = False  # True = Favorites / Recent (non-collapsible)


class ChannelListWidget(QListWidget):
    channel_selected = pyqtSignal(Channel)
    favorite_toggled = pyqtSignal(str)  # emits channel.url

    def __init__(
        self,
        manager: ProfileManager | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._manager = manager
        self._channels: list[Channel] = []
        self._collapsed_groups: set[str] = set()
        self._current_query: str = ""
        self.setStyleSheet(
            "QListWidget { border: none; background: #161616; outline: none; }"
            "QListWidget::item { padding: 8px 12px; color: #e0e0e0; min-height: 24px; }"
            "QListWidget::item:selected { background: #00bcd4; color: #000000; }"
            "QListWidget::item:hover:!selected { background: #222222; }"
        )
        self.itemClicked.connect(self._on_item_clicked)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

    def load_channels(
        self,
        channels: list[Channel],
        favorites: list[str] | None = None,
        recent: list[str] | None = None,
    ) -> None:
        self.clear()
        self._collapsed_groups.clear()
        self._current_query = ""
        self._channels = list(channels)

        url_to_channel: dict[str, Channel] = {ch.url: ch for ch in channels}

        # Pinned group: Favorites
        if favorites:
            self._add_pinned_header("⭐ Favorites", len(favorites))
            for url in favorites:
                ch = url_to_channel.get(url)
                if ch is not None:
                    self._add_channel(ch)

        # Pinned group: Recent
        if recent:
            self._add_pinned_header("🕐 Recent", len(recent))
            for url in recent:
                ch = url_to_channel.get(url)
                if ch is not None:
                    self._add_channel(ch)

        # Normal groups
        groups: dict[str, list[Channel]] = {}
        for ch in channels:
            key = ch.group if ch.group else _UNCATEGORIZED
            groups.setdefault(key, []).append(ch)

        for group_name, group_channels in groups.items():
            self._add_header(group_name, len(group_channels))
            for ch in group_channels:
                self._add_channel(ch)

    def _add_pinned_header(self, text: str, count: int) -> None:
        item = QListWidgetItem(f"{text} ({count})")
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        font = QFont()
        font.setBold(True)
        item.setFont(font)
        item.setForeground(QColor("#9e9e9e"))
        item.setBackground(QColor("#0d0d0d"))
        item.setData(
            Qt.ItemDataRole.UserRole,
            _GroupHeader(name=text, count=count, pinned=True),
        )
        self.addItem(item)

    def _add_header(self, text: str, count: int) -> None:
        item = QListWidgetItem(f"▼ {text} ({count})")
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        font = QFont()
        font.setBold(True)
        item.setFont(font)
        item.setForeground(QColor("#9e9e9e"))
        item.setBackground(QColor("#0d0d0d"))
        item.setData(Qt.ItemDataRole.UserRole, _GroupHeader(name=text, count=count))
        self.addItem(item)

    def _add_channel(self, channel: Channel) -> None:
        item = QListWidgetItem(f"  {channel.name}")
        item.setData(Qt.ItemDataRole.UserRole, channel)
        self.addItem(item)

    def _apply_visibility(self, query: str) -> None:
        """Single-pass visibility update respecting both collapse state and search."""
        q = query.lower().strip()
        current_group: str | None = None
        header_has_visible: dict[int, bool] = {}
        current_header_idx: int | None = None

        for i in range(self.count()):
            item = self.item(i)
            assert item is not None
            data = item.data(Qt.ItemDataRole.UserRole)

            if isinstance(data, _GroupHeader):
                current_group = data.name
                current_header_idx = i
                header_has_visible[i] = False
            elif isinstance(data, Channel):
                if q:
                    visible = q in data.name.lower()
                else:
                    visible = current_group not in self._collapsed_groups
                item.setHidden(not visible)
                if current_header_idx is not None and visible:
                    header_has_visible[current_header_idx] = True

        # Second pass: hide headers that have no visible channels
        for header_idx, has_visible in header_has_visible.items():
            hdr = self.item(header_idx)
            assert hdr is not None
            hdr.setHidden(q != "" and not has_visible)

    def filter_channels(self, text: str) -> None:
        self._current_query = text
        self._apply_visibility(text)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        data = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(data, Channel):
            self.channel_selected.emit(data)
        elif isinstance(data, _GroupHeader) and not data.pinned:
            group_name = data.name
            if group_name in self._collapsed_groups:
                self._collapsed_groups.discard(group_name)
                arrow = "▼"
            else:
                self._collapsed_groups.add(group_name)
                arrow = "▶"
            item.setText(f"{arrow} {group_name} ({data.count})")
            self._apply_visibility(self._current_query)

    def toggle_favorite_for_item(self, item: QListWidgetItem) -> None:
        """Toggle favorite for a channel item and emit favorite_toggled."""
        data = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(data, Channel):
            self.favorite_toggled.emit(data.url)

    def reload_with_profile(self, profile: Profile) -> None:
        """Reload the list with updated favorites/recent from profile."""
        self.load_channels(
            self._channels,
            favorites=profile.favorites,
            recent=profile.recent,
        )

    def _on_context_menu(self, pos: QPoint) -> None:
        item = self.itemAt(pos)
        if item is None:
            return
        data = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(data, Channel):
            return

        favorites: list[str] = []
        if self._manager is not None:
            favorites = self._manager.active_profile().favorites

        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background: #1e1e1e; color: #e0e0e0;"
            " border: 1px solid #2a2a2a; }"
            "QMenu::item:selected { background: #00bcd4; color: #000000; }"
        )
        if data.url in favorites:
            action = menu.addAction("✕ Quitar de Favoritos")
        else:
            action = menu.addAction("★ Agregar a Favoritos")
        assert action is not None
        action.triggered.connect(lambda: self.toggle_favorite_for_item(item))
        menu.exec(self.mapToGlobal(pos))


class ChannelListPanel(QWidget):
    def __init__(
        self,
        manager: ProfileManager | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search channels\u2026")
        self._search.setStyleSheet(
            "QLineEdit { background: #1e1e1e; color: #e0e0e0; "
            "border: 1px solid #2a2a2a; border-radius: 6px; padding: 8px 12px; "
            "font-size: 13px; }"
            "QLineEdit:focus { border-color: #00bcd4; }"
        )
        self.channel_list = ChannelListWidget(manager=manager)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._search)
        layout.addWidget(self.channel_list)

        self._search.textChanged.connect(self.channel_list.filter_channels)

        # Expose signals for external wiring convenience
        self.channel_selected = self.channel_list.channel_selected
        self.favorite_toggled = self.channel_list.favorite_toggled
