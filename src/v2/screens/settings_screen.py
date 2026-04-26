from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

_BG = "#060810"
_SURFACE = "#0c0e18"
_ELEVATED = "#121522"
_BORDER = "rgba(255,255,255,0.06)"
_TEXT = "#e8eaf0"
_DIM = "#555761"
_SEC = "#9698a0"
_ACCENT = "#001999"

_SECTIONS: list[tuple[str, str]] = [
    ("general", "General"),
    ("perfil", "Perfil"),
    ("playlist", "Playlist"),
    ("epg", "EPG"),
    ("parental", "Parental"),
    ("info", "Información"),
]
_SECTION_KEYS = [k for k, _ in _SECTIONS]


class SettingsScreen(QWidget):
    close_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._section = "general"

        self.setStyleSheet(f"background: {_BG};")

        # Top header bar
        header = QWidget()
        header.setFixedHeight(56)
        header.setStyleSheet(
            f"background: {_SURFACE}; border-bottom: 1px solid {_BORDER};"
        )
        header_row = QHBoxLayout(header)
        header_row.setContentsMargins(24, 0, 24, 0)
        h_lbl = QLabel("SETTINGS")
        h_lbl.setStyleSheet(
            f"color: {_TEXT}; font-size: 16px; font-weight: 700; "
            "letter-spacing: -0.01em; background: transparent; border: none;"
        )
        header_row.addWidget(h_lbl)
        header_row.addStretch()

        # Left navigation rail
        rail = QWidget()
        rail.setFixedWidth(200)
        rail.setStyleSheet(
            f"background: {_SURFACE}; border-right: 1px solid {_BORDER};"
        )
        rail_layout = QVBoxLayout(rail)
        rail_layout.setContentsMargins(0, 8, 0, 8)
        rail_layout.setSpacing(1)

        self._rail_btns: dict[str, QPushButton] = {}
        for key, label in _SECTIONS:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setFixedHeight(40)
            btn.setStyleSheet(
                f"QPushButton {{"
                f"  background: transparent; color: {_SEC}; border: none;"
                f"  text-align: left; padding: 0 18px; font-size: 12px;"
                f"  font-weight: 400; border-left: 2px solid transparent;"
                f"}}"
                f"QPushButton:checked {{"
                f"  background: rgba(0,25,153,0.10); color: {_TEXT};"
                f"  border-left: 2px solid {_ACCENT}; font-weight: 600;"
                f"}}"
                f"QPushButton:hover:!checked {{"
                f"  background: rgba(255,255,255,0.03); color: {_TEXT};"
                f"}}"
            )
            btn.clicked.connect(lambda _checked, k=key: self.select_section(k))
            self._rail_btns[key] = btn
            rail_layout.addWidget(btn)
        rail_layout.addStretch()
        self._rail_btns["general"].setChecked(True)

        # Section content stack
        self._section_stack = QStackedWidget()
        self._section_stack.setStyleSheet(f"background: {_BG};")
        for key, label in _SECTIONS:
            self._section_stack.addWidget(self._make_page(key, label))

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(rail)
        body.addWidget(self._section_stack)

        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        main.addWidget(header)
        main.addLayout(body)

    def selected_section(self) -> str:
        return self._section

    def select_section(self, section: str) -> None:
        if section not in _SECTION_KEYS:
            return
        self._section = section
        for key, btn in self._rail_btns.items():
            btn.setChecked(key == section)
        self._section_stack.setCurrentIndex(_SECTION_KEYS.index(section))

    def section_count(self) -> int:
        return len(_SECTIONS)

    def _request_close(self) -> None:
        self.close_requested.emit()

    @staticmethod
    def _make_page(key: str, title: str) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background: {_BG};")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(0)

        tag = QLabel(title.upper())
        tag.setStyleSheet(
            f"color: {_DIM}; font-size: 9px; font-weight: 700;"
            "letter-spacing: 0.15em; background: transparent; border: none;"
        )
        layout.addWidget(tag)
        layout.addSpacing(24)

        desc = QLabel(f"Configuración de {title}")
        desc.setStyleSheet(
            f"color: {_SEC}; font-size: 13px; background: transparent; border: none;"
        )
        layout.addWidget(desc)
        layout.addStretch()
        return page
