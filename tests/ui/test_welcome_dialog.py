import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLineEdit, QPushButton

from src.models.profile import AVATAR_COLORS
from src.ui.welcome_dialog import WelcomeDialog


@pytest.fixture
def dialog(qtbot):
    d = WelcomeDialog()
    qtbot.addWidget(d)
    return d


class TestWelcomeDialogStructure:
    def test_has_name_input(self, dialog):
        assert dialog.findChild(QLineEdit) is not None

    def test_start_button_exists(self, dialog):
        btn = dialog.findChild(QPushButton)
        assert btn is not None

    def test_window_has_no_close_button(self, dialog):
        flags = dialog.windowFlags()
        assert not (flags & Qt.WindowType.WindowCloseButtonHint)

    def test_default_color_is_cyan(self, dialog):
        assert dialog.selected_color == AVATAR_COLORS[0]

    def test_selected_name_empty_by_default(self, dialog):
        assert dialog.selected_name == ""


class TestWelcomeDialogValidation:
    def test_start_button_disabled_when_name_empty(self, dialog):
        btn = dialog.findChild(QPushButton)
        assert btn is not None
        name_input = dialog.findChild(QLineEdit)
        assert name_input is not None
        name_input.clear()
        assert not btn.isEnabled()

    def test_start_button_enabled_when_name_filled(self, dialog):
        btn = dialog.findChild(QPushButton)
        name_input = dialog.findChild(QLineEdit)
        assert name_input is not None
        name_input.setText("Mi Perfil")
        assert btn is not None
        assert btn.isEnabled()

    def test_selected_name_reflects_input(self, dialog):
        name_input = dialog.findChild(QLineEdit)
        assert name_input is not None
        name_input.setText("Gerard")
        assert dialog.selected_name == "Gerard"


class TestWelcomeDialogColors:
    def test_clicking_color_changes_selected_color(self, dialog, qtbot):
        second_color = AVATAR_COLORS[1]
        dialog.select_color(second_color)
        assert dialog.selected_color == second_color

    def test_all_avatar_colors_are_selectable(self, dialog):
        for color in AVATAR_COLORS:
            dialog.select_color(color)
            assert dialog.selected_color == color
