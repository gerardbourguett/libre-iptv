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

from src.models.profile import Profile

_BG = "#060810"
_SURFACE = "#0c0e18"
_ELEVATED = "#121522"
_BORDER = "rgba(255,255,255,0.06)"
_TEXT = "#e8eaf0"
_DIM = "#555761"
_SEC = "#9698a0"
_ACCENT = "#001999"


class _ProfileCard(QFrame):
    clicked = pyqtSignal(object)  # Profile

    def __init__(self, profile: Profile, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._profile = profile
        self.setFixedSize(120, 150)
        self.setStyleSheet(
            f"QFrame {{ background: transparent; border: none; }}"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        color = profile.color or _ACCENT
        initial = (profile.name[:1] or "?").upper()

        avatar = QLabel(initial)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFixedSize(88, 88)
        avatar.setStyleSheet(
            f"background: transparent;"
            f"color: {color};"
            f"font-size: 36px; font-weight: 700;"
            f"border: 2px solid {color};"
        )
        layout.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignCenter)

        name_lbl = QLabel(profile.name)
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setWordWrap(True)
        name_lbl.setStyleSheet(
            f"color: {_SEC}; font-size: 13px; font-weight: 600;"
            "background: transparent; border: none;"
        )
        layout.addWidget(name_lbl)

    @property
    def profile(self) -> Profile:
        return self._profile

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        self.clicked.emit(self._profile)
        super().mousePressEvent(event)


class _AddCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(120, 150)
        self.setStyleSheet(
            f"QFrame {{ background: transparent; border: none; }}"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        plus = QLabel("+")
        plus.setAlignment(Qt.AlignmentFlag.AlignCenter)
        plus.setFixedSize(88, 88)
        plus.setStyleSheet(
            f"background: transparent; color: {_DIM}; font-size: 32px; font-weight: 400;"
            f"border: 1px dashed {_BORDER};"
        )
        layout.addWidget(plus, alignment=Qt.AlignmentFlag.AlignCenter)

        label = QLabel("Add")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        label.setStyleSheet(
            f"color: {_DIM}; font-size: 13px; font-weight: 600;"
            "background: transparent; border: none;"
        )
        layout.addWidget(label)

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        self.clicked.emit()
        super().mousePressEvent(event)


class ProfileScreen(QWidget):
    profile_selected = pyqtSignal(object)  # Profile
    add_profile_requested = pyqtSignal()

    def __init__(
        self,
        profiles: list[Profile] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._cards: list[_ProfileCard] = []
        self._add_card = _AddCard()
        self._add_card.clicked.connect(self.add_profile_requested)

        self.setStyleSheet(f"background: {_BG};")

        # Subtle grid background overlay (achieved via a layered QLabel)
        center_widget = QWidget()
        center_widget.setStyleSheet("background: transparent;")
        center_layout = QVBoxLayout(center_widget)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.setContentsMargins(40, 0, 40, 0)
        center_layout.setSpacing(0)

        # Logo
        logo_row = QHBoxLayout()
        logo_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_row.setSpacing(14)

        logo_box = QLabel("L")
        logo_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_box.setFixedSize(44, 44)
        logo_box.setStyleSheet(
            f"color: {_ACCENT}; font-size: 18px; font-weight: 800;"
            f"border: 2px solid {_ACCENT}; background: transparent;"
        )
        logo_row.addWidget(logo_box)

        logo_text = QLabel("LIBRE<span style='color: #001999'>IPTV</span>")
        logo_text.setTextFormat(Qt.TextFormat.RichText)
        logo_text.setStyleSheet(
            f"color: {_TEXT}; font-size: 26px; font-weight: 800;"
            "letter-spacing: -0.04em; background: transparent; border: none;"
        )
        logo_row.addWidget(logo_text)

        center_layout.addLayout(logo_row)
        center_layout.addSpacing(28)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedWidth(240)
        sep.setStyleSheet(f"background: {_BORDER}; border: none; max-height: 1px;")
        center_layout.addWidget(sep, alignment=Qt.AlignmentFlag.AlignCenter)
        center_layout.addSpacing(28)

        # "SELECT PROFILE" label
        select_lbl = QLabel("SELECT PROFILE")
        select_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        select_lbl.setStyleSheet(
            f"color: {_DIM}; font-size: 11px; font-weight: 600;"
            "letter-spacing: 0.15em; background: transparent; border: none;"
        )
        center_layout.addWidget(select_lbl)
        center_layout.addSpacing(28)

        # Cards container
        self._cards_widget = QWidget()
        self._cards_widget.setStyleSheet("background: transparent;")
        self._cards_layout = QHBoxLayout(self._cards_widget)
        self._cards_layout.setContentsMargins(0, 0, 0, 0)
        self._cards_layout.setSpacing(20)
        self._cards_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background: transparent; }}"
            "QScrollBar:horizontal { height: 0px; }"
        )
        scroll.setWidget(self._cards_widget)
        scroll.setFixedHeight(180)

        center_layout.addWidget(scroll)

        # Footer version
        footer = QLabel("v1.0.0 — MANAGE PROFILES")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(
            f"color: {_DIM}; font-size: 9px; letter-spacing: 0.1em;"
            "background: transparent; border: none;"
        )
        center_layout.addSpacing(40)
        center_layout.addWidget(footer)

        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.addStretch()
        main.addWidget(center_widget)
        main.addStretch()

        if profiles:
            self.load_profiles(profiles)
        else:
            self._rebuild()

    def load_profiles(self, profiles: list[Profile]) -> None:
        self._cards = []
        self._rebuild(profiles)

    def profile_count(self) -> int:
        return len(self._cards)

    def card_names(self) -> list[str]:
        return [c.profile.name for c in self._cards]

    def has_add_card(self) -> bool:
        return self._add_card is not None

    def _rebuild(self, profiles: list[Profile] | None = None) -> None:
        while self._cards_layout.count():
            item = self._cards_layout.takeAt(0)
            if item and item.widget():
                item.widget().setParent(None)

        self._cards.clear()

        for profile in (profiles or []):
            card = _ProfileCard(profile)
            card.clicked.connect(self.profile_selected)
            self._cards_layout.addWidget(card)
            self._cards.append(card)

        self._cards_layout.addWidget(self._add_card)
