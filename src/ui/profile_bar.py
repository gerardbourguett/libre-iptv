from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMenu,
    QSizePolicy,
    QToolButton,
    QWidget,
)

from src.models.profile import Profile
from src.profiles.manager import ProfileManager

_BAR_HEIGHT = 48
_AVATAR_SIZE = 32

_BAR_STYLE = """
QWidget#profile_bar {
    background: #0d0d0d;
    border-bottom: 1px solid #1e1e1e;
}
QToolButton {
    background: transparent;
    color: #9e9e9e;
    border: none;
    padding: 4px 6px;
    font-size: 16px;
}
QToolButton:hover {
    color: #e0e0e0;
}
"""


class _AvatarLabel(QWidget):
    """Circular avatar with the profile's color and name initial."""

    def __init__(self, initial: str, color: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._initial = initial.upper()
        self._color = color
        self.setFixedSize(_AVATAR_SIZE, _AVATAR_SIZE)

    def set_profile(self, initial: str, color: str) -> None:
        self._initial = initial.upper()
        self._color = color
        self.update()

    def initial(self) -> str:
        return self._initial

    def paintEvent(self, event: object) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QColor(self._color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, _AVATAR_SIZE, _AVATAR_SIZE)

        painter.setPen(QColor("#000000"))
        font = QFont()
        font.setBold(True)
        font.setPixelSize(14)
        painter.setFont(font)
        painter.drawText(
            0, 0, _AVATAR_SIZE, _AVATAR_SIZE,
            Qt.AlignmentFlag.AlignCenter,
            self._initial,
        )


class _NameButton(QToolButton):
    """Clickable label showing the active profile name + dropdown arrow."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(
            "QToolButton { color: #e0e0e0; font-size: 13px; font-weight: bold;"
            " background: transparent; border: none; padding: 0 4px; }"
            "QToolButton:hover { color: #ffffff; }"
            "QToolButton::menu-indicator { image: none; }"
        )
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


class ProfileSelectorBar(QWidget):
    """Top bar showing the active profile with switch/add/settings actions."""

    profile_switched = pyqtSignal(Profile)

    def __init__(
        self, manager: ProfileManager, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._manager = manager
        self.setObjectName("profile_bar")
        self.setFixedHeight(_BAR_HEIGHT)
        self.setStyleSheet(_BAR_STYLE)

        self._build_ui()
        self.refresh()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """Sync the bar with the current active profile."""
        profile = self._manager.active_profile()
        self._avatar.set_profile(profile.name[0], profile.color)
        self._name_btn.setText(f"{profile.name}  ▾")
        self._name_btn.setToolTip(f"Perfil activo: {profile.name}")

    def profile_name_text(self) -> str:
        return self._name_btn.text()

    def avatar_initial(self) -> str:
        return self._avatar.initial()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 8, 8)
        layout.setSpacing(8)

        profile = self._manager.active_profile()
        self._avatar = _AvatarLabel(profile.name[0], profile.color)
        layout.addWidget(self._avatar)

        self._name_btn = _NameButton()
        self._name_btn.clicked.connect(self._show_profile_menu)
        layout.addWidget(self._name_btn)

        self._add_btn = QToolButton()
        self._add_btn.setText("+")
        self._add_btn.setToolTip("Nuevo perfil")
        layout.addWidget(self._add_btn)

        self._settings_btn = QToolButton()
        self._settings_btn.setText("⚙")
        self._settings_btn.setToolTip("Configurar perfil")
        layout.addWidget(self._settings_btn)

    def _show_profile_menu(self) -> None:
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background: #1e1e1e; color: #e0e0e0; border: 1px solid #2a2a2a; }"
            "QMenu::item:selected { background: #00bcd4; color: #000000; }"
            "QMenu::item:checked { font-weight: bold; }"
        )
        active_id = self._manager.active_profile().id
        for profile in self._manager.list_profiles():
            action = menu.addAction(profile.name)
            assert action is not None
            action.setCheckable(True)
            action.setChecked(profile.id == active_id)
            action.triggered.connect(
                lambda checked, pid=profile.id: self._on_switch(pid)
            )
        menu.exec(self.mapToGlobal(self._name_btn.geometry().bottomLeft()))

    def _on_switch(self, profile_id: str) -> None:
        if profile_id == self._manager.active_profile().id:
            return
        profile = self._manager.switch_profile(profile_id)
        self.refresh()
        self.profile_switched.emit(profile)
