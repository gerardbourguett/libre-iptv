"""Startup profile chooser — shown every time the app opens."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from src.models.profile import AVATAR_COLORS, Profile
from src.profiles.manager import ProfileManager

_STYLE = """
QDialog { background: #0d0d0d; }
QLabel  { color: #e0e0e0; }
QScrollArea { border: none; background: transparent; }
QWidget#scroll_contents { background: transparent; }
QLineEdit {
    background: #1e1e1e; color: #e0e0e0;
    border: 1px solid #2a2a2a; border-radius: 6px;
    padding: 8px 12px; font-size: 13px;
}
QLineEdit:focus { border-color: #00bcd4; }
QPushButton#primary {
    background: #00bcd4; color: #000; border: none;
    border-radius: 6px; padding: 10px 24px; font-size: 13px; font-weight: bold;
}
QPushButton#primary:disabled { background: #2a2a2a; color: #555; }
QPushButton#primary:hover:enabled { background: #00e5ff; }
QPushButton#new_profile {
    background: transparent; color: #9e9e9e; border: 1px solid #2a2a2a;
    border-radius: 6px; padding: 8px 18px; font-size: 12px;
}
QPushButton#new_profile:hover { color: #e0e0e0; border-color: #555; }
"""

_AVATAR_SIZE = 56


class _ProfileCard(QWidget):
    """Clickable card for a single profile."""

    def __init__(
        self, profile: Profile, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._profile = profile
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(72)
        self.setStyleSheet(
            "QWidget { border-radius: 8px; }"
            "QWidget:hover { background: #1e1e1e; }"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(14)

        # Avatar circle
        avatar = _AvatarWidget(profile.name[0], profile.color)
        layout.addWidget(avatar)

        # Name label
        name_lbl = QLabel(profile.name)
        name_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #e0e0e0;")
        layout.addWidget(name_lbl, stretch=1)

        arrow = QLabel("›")
        arrow.setStyleSheet("color: #555; font-size: 18px;")
        layout.addWidget(arrow)

    def mousePressEvent(self, event: object) -> None:
        if self.parent() is not None:
            dialog = self.window()
            if isinstance(dialog, ProfileChooserDialog):
                dialog.select_profile(self._profile)


class _AvatarWidget(QWidget):
    def __init__(
        self, initial: str, color: str, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._initial = initial.upper()
        self._color = color
        self.setFixedSize(_AVATAR_SIZE, _AVATAR_SIZE)

    def paintEvent(self, event: object) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(self._color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, _AVATAR_SIZE, _AVATAR_SIZE)
        painter.setPen(QColor("#000000"))
        from PyQt6.QtGui import QFont
        font = QFont()
        font.setBold(True)
        font.setPixelSize(22)
        painter.setFont(font)
        painter.drawText(
            0, 0, _AVATAR_SIZE, _AVATAR_SIZE,
            Qt.AlignmentFlag.AlignCenter,
            self._initial,
        )


class _ColorPicker(QWidget):
    def __init__(
        self, selected: str, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._selected = selected
        self._buttons: dict[str, QToolButton] = {}
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        for color in AVATAR_COLORS:
            btn = QToolButton()
            btn.setFixedSize(28, 28)
            btn.setCheckable(True)
            btn.setChecked(color == selected)
            btn.setStyleSheet(
                f"QToolButton {{ background: {color}; border-radius: 14px;"
                " border: 2px solid transparent; }}"
                f"QToolButton:checked {{ border-color: #ffffff; }}"
            )
            btn.clicked.connect(lambda _, c=color: self._pick(c))
            self._buttons[color] = btn
            layout.addWidget(btn)
        layout.addStretch()

    def _pick(self, color: str) -> None:
        self._selected = color
        for c, btn in self._buttons.items():
            btn.setChecked(c == color)

    @property
    def selected(self) -> str:
        return self._selected


class ProfileChooserDialog(QDialog):
    """Startup dialog shown every time. Pick existing profile or create new."""

    def __init__(
        self, manager: ProfileManager, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._manager = manager
        self._selected_profile: Profile | None = None
        self.setWindowTitle("IPTV Player")
        self.setMinimumWidth(440)
        self.setStyleSheet(_STYLE)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
        )
        self._build_ui()

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    @property
    def selected_profile(self) -> Profile | None:
        return self._selected_profile

    def select_profile(self, profile: Profile) -> None:
        """Called by _ProfileCard on click."""
        self._selected_profile = profile
        self._manager.switch_profile(profile.id)
        self.accept()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self._stack_layout = QVBoxLayout(self)
        self._stack_layout.setContentsMargins(0, 0, 0, 0)
        self._stack_layout.setSpacing(0)

        profiles = self._manager.list_profiles()
        if profiles:
            self._build_picker_view(profiles)
        else:
            self._build_create_view()

    def _build_picker_view(self, profiles: list[Profile]) -> None:
        """Main view: list of profiles + button to add new."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title = QLabel("¿Quién sos?")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #e0e0e0;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Scrollable list of profile cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        contents = QWidget()
        contents.setObjectName("scroll_contents")
        cards_layout = QVBoxLayout(contents)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(6)

        for profile in profiles:
            cards_layout.addWidget(_ProfileCard(profile))

        cards_layout.addStretch()
        scroll.setWidget(contents)
        layout.addWidget(scroll)

        new_btn = QPushButton("+ Agregar perfil")
        new_btn.setObjectName("new_profile")
        new_btn.clicked.connect(self._show_create_form)
        layout.addWidget(new_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._stack_layout.addWidget(container)

    def _build_create_view(self) -> None:
        """Form to create the first (or a new) profile."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(18)

        title = QLabel("Bienvenido a IPTV Player")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #e0e0e0;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("Creá tu primer perfil para comenzar.")
        sub.setStyleSheet("color: #888; font-size: 13px;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Nombre del perfil")
        self._name_input.setMaxLength(24)
        layout.addWidget(self._name_input)

        color_lbl = QLabel("Color de avatar:")
        color_lbl.setStyleSheet("color: #9e9e9e; font-size: 12px;")
        layout.addWidget(color_lbl)
        self._color_picker = _ColorPicker(AVATAR_COLORS[0])
        layout.addWidget(self._color_picker)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(spacer)

        self._create_btn = QPushButton("Comenzar")
        self._create_btn.setObjectName("primary")
        self._create_btn.setEnabled(False)
        self._create_btn.clicked.connect(self._on_create)
        layout.addWidget(self._create_btn)

        self._name_input.textChanged.connect(
            lambda t: self._create_btn.setEnabled(bool(t.strip()))
        )

        if hasattr(self, "_stack_layout"):
            # Clear existing widgets and show the form
            while self._stack_layout.count():
                item = self._stack_layout.takeAt(0)
                if item:
                    w = item.widget()
                    if w:
                        w.deleteLater()

        self._stack_layout.addWidget(container)

    def _show_create_form(self) -> None:
        self._build_create_view()

    def _on_create(self) -> None:
        name = self._name_input.text().strip() or "Mi Perfil"
        color = self._color_picker.selected
        profile = self._manager.create_profile(name, color)
        self._selected_profile = profile
        self._manager.switch_profile(profile.id)
        self.accept()
