from __future__ import annotations

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton

from src.i18n import init_translator
from src.ui.pin_dialog import PinDialog


@pytest.fixture(autouse=True)
def translator(qapp):
    init_translator(locales_dir=None)


@pytest.fixture
def dialog(qtbot):
    d = PinDialog()
    qtbot.addWidget(d)
    return d


class TestPinDialogStructure:
    def test_is_modal(self, dialog):
        assert dialog.windowModality() == Qt.WindowModality.ApplicationModal

    def test_has_prompt_label(self, dialog):
        labels = dialog.findChildren(QLabel)
        texts = [lbl.text() for lbl in labels]
        assert any("Ingrese PIN" in t for t in texts)

    def test_has_confirm_button(self, dialog):
        buttons = dialog.findChildren(QPushButton)
        texts = [btn.text() for btn in buttons]
        assert any("Confirmar" in t for t in texts)

    def test_has_cancel_button(self, dialog):
        buttons = dialog.findChildren(QPushButton)
        texts = [btn.text() for btn in buttons]
        assert any("Cancelar" in t for t in texts)

    def test_numeric_buttons_exist(self, dialog):
        buttons = dialog.findChildren(QPushButton)
        digit_texts = [btn.text() for btn in buttons if btn.text().isdigit()]
        assert set(digit_texts) == {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}

    def test_has_dark_theme(self, dialog):
        style = dialog.styleSheet()
        assert "#0d0d0d" in style or "#1e1e1e" in style


class TestPinDialogInput:
    def test_entering_digits_updates_display(self, dialog, qtbot):
        btn = _find_button(dialog, "1")
        qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        assert dialog._pin == "1"

    def test_entering_four_digits(self, dialog, qtbot):
        for digit in "1234":
            btn = _find_button(dialog, digit)
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        assert dialog._pin == "1234"

    def test_display_masks_pin(self, dialog, qtbot):
        for digit in "1234":
            btn = _find_button(dialog, digit)
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        assert "●" in dialog._display.text() or "•" in dialog._display.text()

    def test_backspace_removes_last_digit(self, dialog, qtbot):
        for digit in "123":
            btn = _find_button(dialog, digit)
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        back = _find_button_by_text(dialog, "⌫") or _find_button_by_text(
            dialog, "Borrar"
        )
        if back is not None:
            qtbot.mouseClick(back, Qt.MouseButton.LeftButton)
            assert dialog._pin == "12"

    def test_clear_resets_pin(self, dialog, qtbot):
        for digit in "1234":
            btn = _find_button(dialog, digit)
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        clear = _find_button_by_text(dialog, "C")
        if clear is not None:
            qtbot.mouseClick(clear, Qt.MouseButton.LeftButton)
            assert dialog._pin == ""


class TestPinDialogBehavior:
    def test_confirm_with_four_digits_accepts(self, dialog, qtbot):
        for digit in "1234":
            btn = _find_button(dialog, digit)
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        confirm = _find_button(dialog, "Confirmar")
        with qtbot.waitSignal(dialog.accepted, timeout=1000):
            qtbot.mouseClick(confirm, Qt.MouseButton.LeftButton)
        assert dialog.pin_value() == "1234"

    def test_confirm_with_less_than_four_digits_shows_error(self, dialog, qtbot):
        btn = _find_button(dialog, "1")
        qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        confirm = _find_button(dialog, "Confirmar")
        qtbot.mouseClick(confirm, Qt.MouseButton.LeftButton)
        assert dialog.result() == QDialog.DialogCode.Rejected
        assert (
            "4" in dialog._error_label.text()
            or "dígitos" in dialog._error_label.text()
        )

    def test_cancel_rejects(self, dialog, qtbot):
        cancel = _find_button(dialog, "Cancelar")
        with qtbot.waitSignal(dialog.rejected, timeout=1000):
            qtbot.mouseClick(cancel, Qt.MouseButton.LeftButton)
        assert dialog.pin_value() is None

    def test_cancel_with_partial_pin_returns_none(self, dialog, qtbot):
        for digit in "12":
            btn = _find_button(dialog, digit)
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        cancel = _find_button(dialog, "Cancelar")
        qtbot.mouseClick(cancel, Qt.MouseButton.LeftButton)
        assert dialog.pin_value() is None


class TestPinDialogSpanish:
    def test_no_english_labels(self, dialog):
        forbidden = {"Enter", "OK", "Submit", "Backspace", "Clear"}
        for widget in dialog.findChildren((QLabel, QPushButton)):
            text = widget.text()
            for word in forbidden:
                assert word.lower() not in text.lower(), (
                    f"Found English word '{word}' in '{text}'"
                )


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _find_button(dialog, text: str):
    for btn in dialog.findChildren(QPushButton):
        if btn.text() == text:
            return btn
    pytest.fail(f"Button with text '{text}' not found")


def _find_button_by_text(dialog, text: str):
    for btn in dialog.findChildren(QPushButton):
        if btn.text() == text:
            return btn
    return None
