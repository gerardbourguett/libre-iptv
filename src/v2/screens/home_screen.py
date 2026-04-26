from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.models.channel import Channel
    from src.models.profile import Profile

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


def _channel_color(ch: Channel) -> str:  # type: ignore[return]
    idx = sum(ord(c) for c in ch.name) % len(_PALETTE)
    return _PALETTE[idx]


class ChannelCard(QFrame):
    clicked = pyqtSignal(object)  # Channel

    def __init__(self, channel: Channel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._channel = channel
        color = _channel_color(channel)
        self.setFixedSize(190, 108)
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
        layout.setContentsMargins(12, 0, 12, 10)
        layout.setSpacing(0)

        # item(0): top accent color bar
        top_bar = QFrame()
        top_bar.setFixedHeight(2)
        top_bar.setStyleSheet(f"background: {color}; border: none; margin: 0 -12px;")
        layout.addWidget(top_bar)

        # item(1): channel name — no spacing before so itemAt(1) is the QLabel
        name_lbl = QLabel(channel.name)
        name_lbl.setContentsMargins(0, 8, 0, 0)
        name_lbl.setStyleSheet(
            f"color: {_TEXT}; font-size: 12px; font-weight: 600;"
            "background: transparent; border: none;"
        )
        layout.addWidget(name_lbl)

        # Group / category
        group_lbl = QLabel(channel.group or "")
        group_lbl.setStyleSheet(
            f"color: {_DIM}; font-size: 9px; background: transparent; border: none;"
        )
        layout.addWidget(group_lbl)

        layout.addStretch()

        # Bottom decorative progress bar
        prog_track = QFrame()
        prog_track.setFixedHeight(2)
        prog_track.setStyleSheet(f"background: {_BORDER}; border: none;")
        prog_inner = QHBoxLayout(prog_track)
        prog_inner.setContentsMargins(0, 0, 0, 0)
        prog_fill = QFrame()
        prog_fill.setFixedHeight(2)
        prog_fill.setStyleSheet(f"background: {color}; border: none;")
        prog_inner.addWidget(prog_fill, stretch=4)
        prog_inner.addStretch(6)
        layout.addWidget(prog_track)

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
        layout.setContentsMargins(0, 0, 0, 28)
        layout.setSpacing(0)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 12)

        self._title = QLabel(title)
        self._title.setStyleSheet(
            f"color: {_TEXT}; font-size: 12px; font-weight: 700;"
            "letter-spacing: 0.02em; background: transparent; border: none;"
        )
        header_row.addWidget(self._title)

        count_badge = QLabel(f"  {len(channels)}")
        count_badge.setStyleSheet(
            f"color: {_DIM}; font-size: 10px; background: transparent; border: none;"
        )
        header_row.addWidget(count_badge)
        header_row.addStretch()

        view_all = QLabel("VIEW ALL →")
        view_all.setStyleSheet(
            f"color: {_DIM}; font-size: 10px; letter-spacing: 0.05em;"
            "background: transparent; border: none;"
        )
        header_row.addWidget(view_all)
        layout.addLayout(header_row)

        self._scroll = QScrollArea()
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background: transparent; }}"
        )
        self._scroll.setFixedHeight(120)

        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
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
    load_playlist_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._rows: list[ChannelRow] = []

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(
            f"QScrollArea {{ background: {_BG}; border: none; }}"
            "QScrollBar:vertical { width: 4px; background: transparent; }"
            f"QScrollBar::handle:vertical {{ background: {_BORDER}; }}"
        )

        self._content = QWidget()
        self._content.setStyleSheet(f"background: {_BG};")
        self._layout = QVBoxLayout(self._content)
        self._layout.setContentsMargins(24, 20, 24, 24)
        self._layout.setSpacing(0)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._scroll.setWidget(self._content)

        self._empty = self._build_empty_state()
        self._loading = self._build_loading_state()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._empty)
        outer.addWidget(self._loading)
        outer.addWidget(self._scroll)

        self._show_state("empty")

    # ── Public API ────────────────────────────────────────────────────────

    def populate(self, channels: list[Channel], profile: Profile) -> None:
        for row in self._rows:
            self._layout.removeWidget(row)
            row.deleteLater()
        self._rows.clear()

        if not channels:
            self._show_state("empty")
            return

        self._show_state("channels")

        url_map = {ch.url: ch for ch in channels}

        continue_chs = self._continue_watching(profile, url_map)
        self._add_row("Continuar Viendo", continue_chs)

        favs = [url_map[url] for url in profile.favorites if url in url_map]
        self._add_row("Favoritos", favs)

        groups: dict[str, list[Channel]] = {}
        for ch in channels:
            g = ch.group or "Sin categoría"
            groups.setdefault(g, []).append(ch)

        for group_name, group_channels in sorted(groups.items()):
            self._add_row(group_name, group_channels)

    def set_loading(self, loading: bool) -> None:
        if loading:
            self._show_state("loading")
        else:
            self._show_state("empty")

    # ── Private helpers ───────────────────────────────────────────────────

    def _show_state(self, state: str) -> None:
        self._empty.setVisible(state == "empty")
        self._loading.setVisible(state == "loading")
        self._scroll.setVisible(state == "channels")

    def _build_empty_state(self) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet(f"background: {_BG};")

        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        icon_box = QLabel("L")
        icon_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_box.setFixedSize(56, 56)
        icon_box.setStyleSheet(
            f"color: {_ACCENT}; font-size: 22px; font-weight: 800;"
            f"border: 2px solid {_ACCENT}; background: transparent;"
        )
        layout.addWidget(icon_box, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("No hay canales cargados")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            f"color: {_TEXT}; font-size: 20px; font-weight: 700;"
            "background: transparent; border: none; letter-spacing: -0.02em;"
        )
        layout.addWidget(title)

        subtitle = QLabel("Cargá una lista M3U para empezar a ver tus canales.")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(
            f"color: {_SEC}; font-size: 13px; background: transparent; border: none;"
        )
        layout.addWidget(subtitle)

        btn = QPushButton("CONFIGURAR LISTA M3U")
        btn.setObjectName("btn_load_playlist")
        btn.setFixedHeight(44)
        btn.setFixedWidth(240)
        btn.setStyleSheet(
            f"QPushButton {{"
            f"  background: {_ACCENT}; color: #060810;"
            f"  border: none; padding: 0 24px;"
            f"  font-size: 12px; font-weight: 700; letter-spacing: 0.04em;"
            f"}}"
            f"QPushButton:hover {{ background: #002acc; }}"
            f"QPushButton:pressed {{ background: #001577; }}"
        )
        btn.clicked.connect(self.load_playlist_requested.emit)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return widget

    def _build_loading_state(self) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet(f"background: {_BG};")

        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        spinner = QLabel("◌")
        spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spinner.setStyleSheet(
            f"color: {_ACCENT}; font-size: 36px; background: transparent; border: none;"
        )
        layout.addWidget(spinner)

        label = QLabel("Cargando canales…")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(
            f"color: {_SEC}; font-size: 14px; background: transparent; border: none;"
        )
        layout.addWidget(label)

        return widget

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
