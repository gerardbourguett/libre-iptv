from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.i18n import get_translator, t


class PinDialog(QDialog):
    """Modal dialog for entering a 4-digit numeric PIN."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("parental.dialog_title"))
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._pin = ""
        self._result: str | None = None

        self.setStyleSheet(
            "QDialog { background: #0d0d0d; }"
            "QLabel { color: #e0e0e0; font-size: 14px; }"
            "QPushButton { background: #1e1e1e; color: #e0e0e0;"
            " border: 1px solid #2a2a2a; border-radius: 6px;"
            " padding: 10px 16px; font-size: 14px; min-width: 48px; }"
            "QPushButton:hover { background: #262626; }"
            "QPushButton:pressed { background: #00bcd4; color: #000000; }"
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Prompt
        self._prompt = QLabel(t("parental.enter_pin"))
        self._prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._prompt)

        # Display
        self._display = QLabel("• • • •")
        self._display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._display.setStyleSheet(
            "font-size: 24px; letter-spacing: 8px; color: #00bcd4;"
        )
        layout.addWidget(self._display)

        # Error label
        self._error_label = QLabel("")
        self._error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._error_label.setStyleSheet("color: #f44336; font-size: 12px;")
        layout.addWidget(self._error_label)

        # Keypad
        keypad = QGridLayout()
        keypad.setSpacing(8)
        digits = [
            ("1", 0, 0), ("2", 0, 1), ("3", 0, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2),
            ("0", 3, 1),
        ]
        for text, row, col in digits:
            btn = QPushButton(text)
            btn.clicked.connect(lambda _checked, t=text: self._on_digit(t))
            keypad.addWidget(btn, row, col)

        # Backspace and Clear
        back_btn = QPushButton("⌫")
        back_btn.clicked.connect(self._on_backspace)
        keypad.addWidget(back_btn, 3, 0)

        clear_btn = QPushButton("C")
        clear_btn.clicked.connect(self._on_clear)
        keypad.addWidget(clear_btn, 3, 2)

        layout.addLayout(keypad)

        # Action buttons
        actions = QHBoxLayout()
        actions.setSpacing(12)

        self._confirm_btn = QPushButton(t("parental.confirm"))
        self._confirm_btn.clicked.connect(self._on_confirm)
        actions.addWidget(self._confirm_btn)

        self._cancel_btn = QPushButton(t("parental.cancel"))
        self._cancel_btn.clicked.connect(self.reject)
        actions.addWidget(self._cancel_btn)

        layout.addLayout(actions)

        tr = get_translator()
        if tr is not None:
            tr.language_changed.connect(self._retranslate)

    def _on_digit(self, digit: str) -> None:
        if len(self._pin) < 4:
            self._pin += digit
            self._error_label.setText("")
        self._update_display()

    def _on_backspace(self) -> None:
        self._pin = self._pin[:-1]
        self._error_label.setText("")
        self._update_display()

    def _on_clear(self) -> None:
        self._pin = ""
        self._error_label.setText("")
        self._update_display()

    def _on_confirm(self) -> None:
        if len(self._pin) == 4:
            self._result = self._pin
            self.accept()
        else:
            self._error_label.setText(t("parental.error.pin_length"))

    def _retranslate(self, _code: str) -> None:
        self.setWindowTitle(t("parental.dialog_title"))
        self._prompt.setText(t("parental.enter_pin"))
        self._confirm_btn.setText(t("parental.confirm"))
        self._cancel_btn.setText(t("parental.cancel"))

    def _update_display(self) -> None:
        filled = "● " * len(self._pin)
        empty = "• " * (4 - len(self._pin))
        self._display.setText((filled + empty).strip())

    def pin_value(self) -> str | None:
        """Return the entered PIN if accepted, otherwise None."""
        return self._result

    def reject(self) -> None:
        self._result = None
        super().reject()
