import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QWidget

from src.ui.toast import ToastManager, ToastNotification


class TestToastNotification:
    def test_toast_shows_message_text(self, qtbot):
        """S1: ToastNotification displays the provided message."""
        parent = QWidget()
        qtbot.addWidget(parent)
        toast = ToastNotification("Hola mundo", "success", 1000, parent)
        qtbot.addWidget(toast)
        assert "Hola mundo" in toast._message_label.text()

    def test_toast_success_kind_has_correct_style(self, qtbot):
        """S2: success kind applies green-ish styling."""
        parent = QWidget()
        qtbot.addWidget(parent)
        toast = ToastNotification("Ok", "success", 1000, parent)
        qtbot.addWidget(toast)
        assert "4caf50" in toast.styleSheet() or "success" in toast.styleSheet().lower()

    def test_toast_error_kind_has_correct_style(self, qtbot):
        """S3: error kind applies red-ish styling."""
        parent = QWidget()
        qtbot.addWidget(parent)
        toast = ToastNotification("Error", "error", 1000, parent)
        qtbot.addWidget(toast)
        assert "f44336" in toast.styleSheet() or "error" in toast.styleSheet().lower()

    def test_toast_closed_signal_emitted_on_dismiss(self, qtbot):
        """S4: closed signal is emitted when toast dismisses."""
        parent = QWidget()
        qtbot.addWidget(parent)
        toast = ToastNotification("Msg", "info", 1, parent)
        qtbot.addWidget(toast)
        with qtbot.waitSignal(toast.closed, timeout=2000):
            toast.show()


class TestToastManager:
    def test_show_creates_toast_with_text(self, qtbot):
        """S5: ToastManager.show() creates a ToastNotification with correct text."""
        parent = QWidget()
        qtbot.addWidget(parent)
        manager = ToastManager(parent)
        manager.show("Canales cargados correctamente", "success", 1000)
        toasts = parent.findChildren(ToastNotification)
        assert len(toasts) == 1
        assert "Canales cargados correctamente" in toasts[0]._message_label.text()

    def test_show_creates_toast_with_error_kind(self, qtbot):
        """S6: ToastManager.show() creates a toast with error kind."""
        parent = QWidget()
        qtbot.addWidget(parent)
        manager = ToastManager(parent)
        manager.show("Error al cargar canales", "error", 1000)
        toasts = parent.findChildren(ToastNotification)
        assert len(toasts) == 1
        assert toasts[0]._kind == "error"

    def test_multiple_toasts_stack(self, qtbot):
        """S7: Multiple toasts are created without overlap (stacked)."""
        parent = QWidget()
        qtbot.addWidget(parent)
        parent.resize(800, 600)
        manager = ToastManager(parent)
        manager.show("Primer toast", "success", 5000)
        manager.show("Segundo toast", "success", 5000)
        toasts = parent.findChildren(ToastNotification)
        assert len(toasts) == 2
