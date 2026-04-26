from __future__ import annotations

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

from src.models.channel import Channel

_BG = "#060810"
_SURFACE = "#0c0e18"
_ELEVATED = "#121522"
_BORDER = "rgba(255,255,255,0.06)"
_TEXT = "#e8eaf0"
_DIM = "#555761"
_SEC = "#9698a0"
_ACCENT = "#001999"

_PALETTE = [
    "#00bcd4", "#2a9d8f", "#d4a017", "#ff7043",
    "#7c3aed", "#059669", "#dc2626", "#0ea5e9",
    "#f59e0b", "#8b5cf6", "#10b981", "#ef4444",
]


def _channel_color(ch: Channel) -> str:
    idx = sum(ord(c) for c in ch.name) % len(_PALETTE)
    return _PALETTE[idx]


class _VodCard(QFrame):
    clicked = pyqtSignal(object)  # Channel

    def __init__(self, channel: Channel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._channel = channel
        color = _channel_color(channel)
        self.setFixedSize(140, 200)

        # No border-radius — flat card style
        self.setStyleSheet(
            f"QFrame {{"
            f"  background: {_ELEVATED};"
            f"  border: 1px solid {_BORDER};"
            f"}}"
            f"QFrame:hover {{"
            f"  border-color: {color}55;"
            f"}}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Top color bar
        top_bar = QFrame()
        top_bar.setFixedHeight(3)
        top_bar.setStyleSheet(f"background: {color}; border: none;")
        layout.addWidget(top_bar)

        # Poster body
        poster_body = QWidget()
        poster_body.setStyleSheet("background: transparent;")
        poster_layout = QVBoxLayout(poster_body)
        poster_layout.setContentsMargins(10, 10, 10, 10)
        poster_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Large letter watermark
        initials = (channel.name[:1]).upper()
        watermark = QLabel(initials)
        watermark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        watermark.setStyleSheet(
            f"color: {color}; font-size: 52px; font-weight: 800;"
            "background: transparent; border: none; opacity: 0.18;"
        )
        poster_layout.addWidget(watermark)

        layout.addWidget(poster_body, stretch=1)

        # Bottom info
        info = QWidget()
        info.setStyleSheet(f"background: {_SURFACE}; border: none;")
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(8, 6, 8, 8)
        info_layout.setSpacing(2)

        name_lbl = QLabel(channel.name)
        name_lbl.setStyleSheet(
            f"color: {_TEXT}; font-size: 11px; font-weight: 600;"
            "background: transparent; border: none;"
        )
        name_lbl.setWordWrap(False)

        group_lbl = QLabel(channel.group or "VOD")
        group_lbl.setStyleSheet(
            f"color: {_DIM}; font-size: 9px; background: transparent; border: none;"
        )

        info_layout.addWidget(name_lbl)
        info_layout.addWidget(group_lbl)
        layout.addWidget(info)

    @property
    def channel(self) -> Channel:
        return self._channel

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        self.clicked.emit(self._channel)
        super().mousePressEvent(event)


class _GroupRow(QWidget):
    channel_selected = pyqtSignal(object)  # Channel

    def __init__(
        self,
        title: str,
        channels: list[Channel],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._title = title
        self._channels = channels

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 24)
        layout.setSpacing(0)

        # Row header
        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 12)

        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet(
            f"color: {_TEXT}; font-size: 12px; font-weight: 700;"
            "letter-spacing: 0.03em; background: transparent; border: none;"
        )
        header_row.addWidget(title_lbl)

        count_lbl = QLabel(f"  {len(channels)}")
        count_lbl.setStyleSheet(
            f"color: {_DIM}; font-size: 10px; background: transparent; border: none;"
        )
        header_row.addWidget(count_lbl)
        header_row.addStretch()

        view_all = QLabel("VER TODO →")
        view_all.setStyleSheet(
            f"color: {_DIM}; font-size: 10px; letter-spacing: 0.05em;"
            "background: transparent; border: none;"
        )
        header_row.addWidget(view_all)

        layout.addLayout(header_row)

        # Horizontal scroll of cards
        scroll = QScrollArea()
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background: transparent; }}"
            "QScrollBar:horizontal { height: 4px; background: transparent; }"
            f"QScrollBar::handle:horizontal {{ background: {_BORDER}; }}"
        )
        scroll.setFixedHeight(228)  # 200px card + 28px padding

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        row = QHBoxLayout(inner)
        row.setContentsMargins(0, 0, 12, 0)
        row.setSpacing(12)

        for ch in channels:
            card = _VodCard(ch)
            card.clicked.connect(self.channel_selected)
            row.addWidget(card)
        row.addStretch()

        scroll.setWidget(inner)
        layout.addWidget(scroll)


class VodScreen(QWidget):
    channel_selected = pyqtSignal(object)  # Channel

    def __init__(
        self,
        channels: list[Channel] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._channels: list[Channel] = []
        self._rows: list[_GroupRow] = []

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
        h_lbl = QLabel("VIDEO ON DEMAND")
        h_lbl.setStyleSheet(
            f"color: {_TEXT}; font-size: 16px; font-weight: 700;"
            "letter-spacing: -0.01em; background: transparent; border: none;"
        )
        header_row.addWidget(h_lbl)
        badge = QLabel("Desde tu M3U")
        badge.setStyleSheet(
            f"color: {_DIM}; font-size: 10px; background: transparent;"
            f"border: 1px solid {_BORDER}; padding: 2px 8px; border: none;"
        )
        header_row.addWidget(badge)
        header_row.addStretch()

        # Scrollable content
        self._content_widget = QWidget()
        self._content_widget.setStyleSheet(f"background: {_BG};")
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(24, 20, 24, 24)
        self._content_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background: {_BG}; }}"
            "QScrollBar:vertical { width: 4px; background: transparent; }"
            f"QScrollBar::handle:vertical {{ background: {_BORDER}; }}"
        )
        scroll.setWidget(self._content_widget)

        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        main.addWidget(header)
        main.addWidget(scroll)

        if channels:
            self.load_channels(channels)

    def load_channels(self, channels: list[Channel]) -> None:
        self._channels = list(channels)
        self._rebuild()

    def _rebuild(self) -> None:
        for row in self._rows:
            self._content_layout.removeWidget(row)
            row.deleteLater()
        self._rows.clear()

        vod_by_group: dict[str, list[Channel]] = {}
        series_by_group: dict[str, list[Channel]] = {}

        for ch in self._channels:
            if ch.is_series:
                series_by_group.setdefault(ch.group or "Series", []).append(ch)
            elif ch.is_vod:
                vod_by_group.setdefault(ch.group or "Películas", []).append(ch)

        for group_name, chs in sorted(vod_by_group.items()):
            row = _GroupRow(group_name, chs)
            row.channel_selected.connect(self.channel_selected)
            self._content_layout.addWidget(row)
            self._rows.append(row)

        for group_name, chs in sorted(series_by_group.items()):
            row = _GroupRow(group_name, chs)
            row.channel_selected.connect(self.channel_selected)
            self._content_layout.addWidget(row)
            self._rows.append(row)

        if not self._rows:
            empty = QLabel("No hay contenido VOD en esta lista.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(
                f"color: {_DIM}; font-size: 13px; padding: 60px;"
                "background: transparent; border: none;"
            )
            self._content_layout.addWidget(empty)

        self._content_layout.addStretch()

    def vod_channels(self) -> list[Channel]:
        return [ch for ch in self._channels if ch.is_vod]

    def series_channels(self) -> list[Channel]:
        return [ch for ch in self._channels if ch.is_series]
