from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from src.i18n import get_translator, t
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


_DIALOG_STYLE = (
    "QDialog { background: #0d0d0d; }"
    "QLabel { color: #e0e0e0; }"
    "QLineEdit { background: #1e1e1e; color: #e0e0e0; border: 1px solid #2a2a2a;"
    " border-radius: 6px; padding: 8px 12px; font-size: 13px; }"
    "QLineEdit:focus { border-color: #00bcd4; }"
    "QDialogButtonBox QPushButton { background: #1e1e1e; color: #e0e0e0;"
    " border: 1px solid #2a2a2a; border-radius: 6px; padding: 6px 18px; }"
    "QDialogButtonBox QPushButton:default { background: #00bcd4; color: #000;"
    " border-color: #00bcd4; }"
)


class _ColorPicker(QWidget):
    """Row of circular color buttons."""

    def __init__(
        self, selected: str, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._selected = selected
        self._buttons: dict[str, QToolButton] = {}
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        from src.models.profile import AVATAR_COLORS

        for color in AVATAR_COLORS:
            btn = QToolButton()
            btn.setFixedSize(28, 28)
            btn.setCheckable(True)
            btn.setChecked(color == selected)
            btn.setStyleSheet(
                f"QToolButton {{ background: {color}; border-radius: 14px;"
                " border: 2px solid transparent; }"
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


class NewProfileDialog(QDialog):
    """Dialog to create a new profile."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("profile.new_dialog_title"))
        self.setMinimumWidth(360)
        self.setStyleSheet(_DIALOG_STYLE)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        layout.addWidget(QLabel(t("profile.name_label")))
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText(t("profile.name_placeholder"))
        self._name_input.setMaxLength(24)
        layout.addWidget(self._name_input)

        layout.addWidget(QLabel(t("profile.color_label")))
        from src.models.profile import AVATAR_COLORS
        self._color_picker = _ColorPicker(AVATAR_COLORS[0])
        layout.addWidget(self._color_picker)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        ok_btn = buttons.button(QDialogButtonBox.StandardButton.Ok)
        assert ok_btn is not None
        self._ok_btn: QPushButton = ok_btn
        self._ok_btn.setEnabled(False)
        self._ok_btn.setDefault(True)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._name_input.textChanged.connect(
            lambda text: self._ok_btn.setEnabled(bool(text.strip()))
        )

    @property
    def selected_name(self) -> str:
        return self._name_input.text().strip()

    @property
    def selected_color(self) -> str:
        return self._color_picker.selected


class ProfileSettingsDialog(QDialog):
    """Dialog to rename, recolor, or delete the active profile."""

    delete_requested = pyqtSignal()

    def __init__(
        self,
        profile: Profile,
        can_delete: bool,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("profile.settings_dialog_title"))
        self.setMinimumWidth(360)
        self.setStyleSheet(_DIALOG_STYLE)
        self._profile = profile
        self._can_delete = can_delete
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        layout.addWidget(QLabel(t("profile.rename_label")))
        self._name_input = QLineEdit(self._profile.name)
        self._name_input.setMaxLength(24)
        layout.addWidget(self._name_input)

        layout.addWidget(QLabel(t("profile.color_label")))
        self._color_picker = _ColorPicker(self._profile.color)
        layout.addWidget(self._color_picker)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        save_btn = buttons.button(QDialogButtonBox.StandardButton.Save)
        assert save_btn is not None
        save_btn.setDefault(True)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if self._can_delete:
            delete_btn = QPushButton(t("profile.delete_button"))
            delete_btn.setStyleSheet(
                "QPushButton { background: #c62828; color: #fff;"
                " border: none; border-radius: 6px; padding: 6px 18px; }"
                "QPushButton:hover { background: #e53935; }"
            )
            delete_btn.clicked.connect(self._on_delete)
            layout.addWidget(delete_btn)

    def _on_delete(self) -> None:
        reply = QMessageBox.question(
            self,
            t("profile.delete_confirm_title"),
            t("profile.delete_confirm_text", name=self._profile.name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit()
            self.reject()

    @property
    def selected_name(self) -> str:
        return self._name_input.text().strip() or self._profile.name

    @property
    def selected_color(self) -> str:
        return self._color_picker.selected


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
        self._name_btn.setToolTip(t("profile.active_tooltip", name=profile.name))

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
        self._add_btn.setToolTip(t("profile.new_tooltip"))
        self._add_btn.clicked.connect(self._on_add_profile)
        layout.addWidget(self._add_btn)

        self._settings_btn = QToolButton()
        self._settings_btn.setText("⚙")
        self._settings_btn.setToolTip(t("profile.settings_tooltip"))
        self._settings_btn.clicked.connect(self._on_settings)
        layout.addWidget(self._settings_btn)

        tr = get_translator()
        if tr is not None:
            tr.language_changed.connect(self._retranslate)

    def _retranslate(self, _code: str) -> None:
        self._add_btn.setToolTip(t("profile.new_tooltip"))
        self._settings_btn.setToolTip(t("profile.settings_tooltip"))
        profile = self._manager.active_profile()
        self._name_btn.setToolTip(t("profile.active_tooltip", name=profile.name))

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

    def _on_add_profile(self) -> None:
        dialog = NewProfileDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        name = dialog.selected_name
        if not name:
            return
        profile = self._manager.create_profile(name, dialog.selected_color)
        self._manager.switch_profile(profile.id)
        self.refresh()
        self.profile_switched.emit(profile)

    def _on_settings(self) -> None:
        profile = self._manager.active_profile()
        can_delete = len(self._manager.list_profiles()) > 1
        dialog = ProfileSettingsDialog(profile, can_delete=can_delete, parent=self)
        dialog.delete_requested.connect(self._on_delete_profile)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        # Apply rename / recolor
        new_name = dialog.selected_name
        new_color = dialog.selected_color
        if new_name == profile.name and new_color == profile.color:
            return
        # Rebuild the profile with new values
        from src.models.profile import Profile as ProfileModel
        updated = ProfileModel(
            id=profile.id,
            name=new_name,
            color=new_color,
            playlist_url=profile.playlist_url,
            playlist_path=profile.playlist_path,
            favorites=profile.favorites,
            recent=profile.recent,
            last_channel_url=profile.last_channel_url,
        )
        self._manager._profiles[profile.id] = updated
        self._manager.save_active()
        self.refresh()

    def _on_delete_profile(self) -> None:
        profile_id = self._manager.active_profile().id
        self._manager.delete_profile(profile_id)
        new_profile = self._manager.active_profile()
        self.refresh()
        self.profile_switched.emit(new_profile)
