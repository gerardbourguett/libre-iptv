from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
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


class SearchScreen(QWidget):
    channel_selected = pyqtSignal(object)  # Channel

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._channels: list[Channel] = []

        self.setStyleSheet(f"background: {_BG};")

        # Header
        header = QWidget()
        header.setFixedHeight(56)
        header.setStyleSheet(
            f"background: {_SURFACE}; border-bottom: 1px solid {_BORDER};"
        )
        header_row = QHBoxLayout(header)
        header_row.setContentsMargins(24, 0, 24, 0)
        h_lbl = QLabel("SEARCH")
        h_lbl.setStyleSheet(
            f"color: {_TEXT}; font-size: 16px; font-weight: 700; "
            "letter-spacing: -0.01em; background: transparent; border: none;"
        )
        header_row.addWidget(h_lbl)
        header_row.addStretch()

        # Search input frame
        search_frame = QFrame()
        search_frame.setFixedHeight(48)
        search_frame.setStyleSheet(
            f"QFrame {{ background: {_ELEVATED}; border: 1px solid {_BORDER}; }}"
        )
        sf_row = QHBoxLayout(search_frame)
        sf_row.setContentsMargins(14, 0, 14, 0)
        sf_row.setSpacing(10)

        icon_lbl = QLabel("⌕")
        icon_lbl.setStyleSheet(
            f"color: {_DIM}; font-size: 16px; background: transparent; border: none;"
        )
        sf_row.addWidget(icon_lbl)

        self._query_input = QLineEdit()
        self._query_input.setPlaceholderText("Buscar canales, programas, categorías...")
        self._query_input.setStyleSheet(
            f"background: transparent; color: {_TEXT}; border: none; "
            f"font-size: 14px; padding: 0; selection-background-color: {_ACCENT};"
        )
        self._query_input.textChanged.connect(self._filter)
        sf_row.addWidget(self._query_input)

        search_wrap = QWidget()
        search_wrap.setStyleSheet(f"background: {_BG};")
        sw_layout = QVBoxLayout(search_wrap)
        sw_layout.setContentsMargins(24, 16, 24, 4)
        sw_layout.addWidget(search_frame)

        # Results list
        self._results_list = QListWidget()
        self._results_list.setStyleSheet(
            f"QListWidget {{ border: none; background: {_BG}; outline: none; }}"
            f"QListWidget::item {{"
            f"  padding: 12px 24px; color: {_TEXT}; min-height: 24px;"
            f"  border-bottom: 1px solid {_BORDER};"
            f"}}"
            f"QListWidget::item:selected {{"
            f"  background: rgba(0,25,153,0.12); color: {_TEXT};"
            f"}}"
            f"QListWidget::item:hover:!selected {{"
            f"  background: rgba(255,255,255,0.03);"
            f"}}"
        )
        self._results_list.itemClicked.connect(self._on_item_clicked)

        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        main.addWidget(header)
        main.addWidget(search_wrap)
        main.addWidget(self._results_list)

    def load_channels(self, channels: list[Channel]) -> None:
        self._channels = list(channels)
        self._results_list.clear()

    def set_query(self, text: str) -> None:
        self._query_input.setText(text)

    def result_count(self) -> int:
        return self._results_list.count()

    def _filter(self, query: str) -> None:
        self._results_list.clear()
        q = query.strip().lower()
        if not q:
            return
        for ch in self._channels:
            if q in ch.name.lower():
                item = QListWidgetItem(ch.name)
                item.setData(Qt.ItemDataRole.UserRole, ch)
                self._results_list.addItem(item)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        ch = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(ch, Channel):
            self.channel_selected.emit(ch)
