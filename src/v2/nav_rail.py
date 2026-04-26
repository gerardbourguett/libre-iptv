from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, QEvent, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QEnterEvent
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.models.profile import Profile

_SURFACE = "#0c0e18"
_BORDER = "rgba(255,255,255,0.06)"
_TEXT = "#e8eaf0"
_DIM = "#555761"
_SEC = "#9698a0"
_ACCENT = "#001999"
_ACCENT_10 = "rgba(0,25,153,0.08)"
_HOVER = "rgba(255,255,255,0.03)"

_NAV_ITEMS: list[tuple[str, str, str]] = [
    ("home", "Home", "H"),
    ("live_tv", "Live TV", "L"),
    ("epg", "Guide", "G"),
    ("vod", "VOD", "V"),
    ("search", "Search", "/"),
]


class _NavButton(QWidget):
    nav_clicked = pyqtSignal(str)

    def __init__(
        self,
        screen: str,
        label: str,
        shortcut: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._screen = screen
        self._active = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 9, 12, 9)
        layout.setSpacing(10)

        self._label_w = QLabel(label)
        layout.addWidget(self._label_w)
        layout.addStretch()

        sc = QLabel(shortcut)
        sc.setStyleSheet(
            f"color: {_DIM}; font-size: 10px; font-family: monospace;"
            "background: transparent; border: none;"
        )
        layout.addWidget(sc)

        self._apply_style()

    def set_active(self, active: bool) -> None:
        self._active = active
        self._apply_style()

    def _apply_style(self) -> None:
        if self._active:
            self.setStyleSheet(
                f"background: {_ACCENT_10}; border-left: 2px solid {_ACCENT};"
            )
            self._label_w.setStyleSheet(
                f"color: {_ACCENT}; font-size: 13px; font-weight: 600;"
                "background: transparent; border: none;"
            )
        else:
            self.setStyleSheet(
                "background: transparent; border-left: 2px solid transparent;"
            )
            self._label_w.setStyleSheet(
                f"color: {_SEC}; font-size: 13px; font-weight: 400;"
                "background: transparent; border: none;"
            )

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        self.nav_clicked.emit(self._screen)
        super().mousePressEvent(event)

    def enterEvent(self, event: QEnterEvent | None) -> None:
        if not self._active:
            self.setStyleSheet(
                f"background: {_HOVER}; border-left: 2px solid transparent;"
            )
            self._label_w.setStyleSheet(
                f"color: {_TEXT}; font-size: 13px; font-weight: 400;"
                "background: transparent; border: none;"
            )
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent | None) -> None:
        if not self._active:
            self._apply_style()
        super().leaveEvent(event)


class NavRail(QWidget):
    navigate_requested = pyqtSignal(str)

    def __init__(
        self,
        profile: Profile | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._buttons: dict[str, _NavButton] = {}
        self._profile = profile

        self.setFixedWidth(200)
        self.setStyleSheet(
            f"NavRail {{ background: {_SURFACE}; border-right: 1px solid {_BORDER}; }}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_logo())

        nav_area = QWidget()
        nav_area.setStyleSheet("background: transparent;")
        nav_layout = QVBoxLayout(nav_area)
        nav_layout.setContentsMargins(6, 8, 6, 8)
        nav_layout.setSpacing(1)

        for screen_id, label, shortcut in _NAV_ITEMS:
            btn = _NavButton(screen_id, label, shortcut)
            btn.nav_clicked.connect(self.navigate_requested)
            nav_layout.addWidget(btn)
            self._buttons[screen_id] = btn

        nav_layout.addStretch()
        layout.addWidget(nav_area, stretch=1)
        layout.addWidget(self._build_bottom())

    def set_active(self, screen: str) -> None:
        for name, btn in self._buttons.items():
            btn.set_active(name == screen)

    def _build_logo(self) -> QWidget:
        w = QWidget()
        w.setFixedHeight(56)
        w.setStyleSheet(
            f"background: {_SURFACE}; border-bottom: 1px solid {_BORDER};"
        )
        row = QHBoxLayout(w)
        row.setContentsMargins(14, 0, 14, 0)
        row.setSpacing(10)

        box = QLabel("L")
        box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box.setFixedSize(28, 28)
        box.setStyleSheet(
            f"color: {_ACCENT}; font-size: 12px; font-weight: 800;"
            f"border: 1.5px solid {_ACCENT}; background: transparent;"
        )
        row.addWidget(box)

        text = QLabel("LIBRE<span style='color:#001999'>IPTV</span>")
        text.setTextFormat(Qt.TextFormat.RichText)
        text.setStyleSheet(
            f"color: {_TEXT}; font-size: 14px; font-weight: 700;"
            "letter-spacing: -0.02em; background: transparent; border: none;"
        )
        row.addWidget(text)
        return w

    def _build_bottom(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(
            f"background: {_SURFACE}; border-top: 1px solid {_BORDER};"
        )
        layout = QVBoxLayout(w)
        layout.setContentsMargins(6, 8, 6, 8)
        layout.setSpacing(1)

        settings_btn = _NavButton("settings", "Settings", "")
        settings_btn.nav_clicked.connect(self.navigate_requested)
        layout.addWidget(settings_btn)
        self._buttons["settings"] = settings_btn

        layout.addWidget(self._build_profile_row())
        return w

    def _build_profile_row(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        row = QHBoxLayout(w)
        row.setContentsMargins(12, 9, 12, 9)
        row.setSpacing(10)

        initial = (self._profile.name[:1] if self._profile else "?").upper()
        color = (
            getattr(self._profile, "color", None) or _ACCENT
            if self._profile
            else _DIM
        )

        avatar = QLabel(initial)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFixedSize(26, 26)
        avatar.setStyleSheet(
            f"color: {color}; font-size: 12px; font-weight: 700;"
            f"border: 1.5px solid {color}; background: transparent;"
        )
        row.addWidget(avatar)

        col = QVBoxLayout()
        col.setSpacing(0)
        col.setContentsMargins(0, 0, 0, 0)
        name_lbl = QLabel(self._profile.name if self._profile else "Sin perfil")
        name_lbl.setStyleSheet(
            f"color: {_TEXT}; font-size: 12px; font-weight: 600;"
            "background: transparent; border: none;"
        )
        switch_lbl = QLabel("SWITCH")
        switch_lbl.setStyleSheet(
            f"color: {_DIM}; font-size: 9px; letter-spacing: 0.08em;"
            "background: transparent; border: none;"
        )
        col.addWidget(name_lbl)
        col.addWidget(switch_lbl)
        row.addLayout(col)

        w.mousePressEvent = lambda _: self.navigate_requested.emit("profiles")  # type: ignore[method-assign]
        return w
