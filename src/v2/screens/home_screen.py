from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.models.channel import Channel
    from src.models.profile import Profile


class ChannelCard(QFrame):
    clicked = pyqtSignal(object)  # Channel

    def __init__(self, channel: Channel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._channel = channel
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet("background-color: #1e1e1e; border-radius: 6px;")
        self.setFixedSize(160, 120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._logo = QLabel()
        self._logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._logo.setStyleSheet("background: transparent;")
        if channel.tvg_logo:
            # Placeholder styling; actual logo loading can be wired externally
            self._logo.setText("📺")
        else:
            self._logo.setText("📺")
        layout.addWidget(self._logo)

        self._name = QLabel(channel.name)
        self._name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._name.setStyleSheet(
            "color: #e0e0e0; background: transparent; font-size: 12px;"
        )
        layout.addWidget(self._name)

    @property
    def channel(self) -> Channel:
        return self._channel

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        self.clicked.emit(self._channel)
        super().mousePressEvent(event)


class ChannelRow(QWidget):
    channel_clicked = pyqtSignal(object)  # Channel

    def __init__(
        self,
        title: str,
        channels: list[Channel],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._channels = channels
        self.setVisible(bool(channels))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        self._title = QLabel(title)
        self._title.setStyleSheet(
            "color: #e0e0e0; font-size: 16px; font-weight: bold; "
            "background: transparent;"
        )
        layout.addWidget(self._title)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("background: transparent; border: none;")

        self._container = QWidget()
        hbox = QHBoxLayout(self._container)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(10)
        hbox.setAlignment(Qt.AlignmentFlag.AlignLeft)

        for ch in channels:
            card = ChannelCard(ch)
            card.clicked.connect(self.channel_clicked.emit)
            hbox.addWidget(card)

        hbox.addStretch()
        self._scroll.setWidget(self._container)
        layout.addWidget(self._scroll)

    def title(self) -> str:
        return self._title.text()


class HomeScreen(QWidget):
    channel_clicked = pyqtSignal(object)  # Channel

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._rows: list[ChannelRow] = []

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("background-color: #0d0d0d; border: none;")

        self._content = QWidget()
        self._layout = QVBoxLayout(self._content)
        self._layout.setContentsMargins(12, 12, 12, 12)
        self._layout.setSpacing(16)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._scroll.setWidget(self._content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._scroll)

    def populate(self, channels: list[Channel], profile: Profile) -> None:
        # Clear existing rows
        for row in self._rows:
            self._layout.removeWidget(row)
            row.deleteLater()
        self._rows.clear()

        url_map = {ch.url: ch for ch in channels}

        # Continue Watching
        continue_chs = self._continue_watching(profile, url_map)
        self._add_row("Continuar Viendo", continue_chs)

        # Favorites
        favs = [url_map[url] for url in profile.favorites if url in url_map]
        self._add_row("Favoritos", favs)

        # Groups
        groups: dict[str, list[Channel]] = {}
        for ch in channels:
            g = ch.group or "Sin categoría"
            groups.setdefault(g, []).append(ch)

        for group_name, group_channels in sorted(groups.items()):
            self._add_row(group_name, group_channels)

    def _add_row(self, title: str, channels: list[Channel]) -> None:
        if not channels:
            return
        row = ChannelRow(title, channels)
        row.channel_clicked.connect(self.channel_clicked.emit)
        self._layout.addWidget(row)
        self._rows.append(row)

    def _continue_watching(
        self,
        profile: Profile,
        url_map: dict[str, Channel],
    ) -> list[Channel]:
        hist = sorted(
            getattr(profile, "history", []),
            key=lambda h: h.watched_at,
            reverse=True,
        )[:20]
        result = []
        for h in hist:
            ch = url_map.get(h.channel_id)
            if ch is not None:
                result.append(ch)
        return result
