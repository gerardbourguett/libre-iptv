from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from src.i18n import t
from src.models.profile import AVATAR_COLORS

_DIALOG_STYLE = """
QDialog {
    background: #0d0d0d;
}
QLabel {
    color: #e0e0e0;
}
QLineEdit {
    background: #1e1e1e;
    color: #e0e0e0;
    border: 1px solid #2a2a2a;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 14px;
}
QLineEdit:focus {
    border-color: #00bcd4;
}
QPushButton#start_btn {
    background: #00bcd4;
    color: #000000;
    border: none;
    border-radius: 6px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: bold;
}
QPushButton#start_btn:disabled {
    background: #2a2a2a;
    color: #555555;
}
QPushButton#start_btn:hover:enabled {
    background: #00e5ff;
}
"""

_COLOR_BTN_SIZE = 32


class _ColorButton(QToolButton):
    """Circular color picker button."""

    def __init__(self, color: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color = color
        self._selected = False
        self.setFixedSize(_COLOR_BTN_SIZE, _COLOR_BTN_SIZE)
        self.setCheckable(True)
        self.setStyleSheet("QToolButton { border: none; background: transparent; }")

    def paintEvent(self, event: object) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(self._color)
        painter.setBrush(color)
        if self.isChecked():
            painter.setPen(QColor("#ffffff"))
            painter.drawEllipse(2, 2, _COLOR_BTN_SIZE - 4, _COLOR_BTN_SIZE - 4)
        else:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(4, 4, _COLOR_BTN_SIZE - 8, _COLOR_BTN_SIZE - 8)


class WelcomeDialog(QDialog):
    """First-run dialog to create the initial user profile."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("app.title"))
        self.setMinimumWidth(420)
        self.setStyleSheet(_DIALOG_STYLE)

        # Remove close button — user MUST complete this dialog
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
        )

        self._selected_color = AVATAR_COLORS[0]
        self._color_buttons: dict[str, _ColorButton] = {}

        self._build_ui()

    # ------------------------------------------------------------------
    # Public properties
    # ------------------------------------------------------------------

    @property
    def selected_name(self) -> str:
        return self._name_input.text().strip()

    @property
    def selected_color(self) -> str:
        return self._selected_color

    def select_color(self, color: str) -> None:
        """Programmatically select a color (used in tests and internally)."""
        self._selected_color = color
        for c, btn in self._color_buttons.items():
            btn.setChecked(c == color)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Title
        title = QLabel(t("welcome.title"))
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #e0e0e0;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel(t("welcome.subtitle"))
        subtitle.setStyleSheet("color: #888888; font-size: 13px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Name input
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText(t("welcome.name_placeholder"))
        self._name_input.setMaxLength(24)
        layout.addWidget(self._name_input)

        # Color picker
        color_label = QLabel(t("welcome.color_label"))
        color_label.setStyleSheet("color: #9e9e9e; font-size: 12px;")
        layout.addWidget(color_label)

        color_row = QWidget()
        color_layout = QHBoxLayout(color_row)
        color_layout.setContentsMargins(0, 0, 0, 0)
        color_layout.setSpacing(8)

        for color in AVATAR_COLORS:
            btn = _ColorButton(color)
            btn.clicked.connect(lambda checked, c=color: self.select_color(c))
            self._color_buttons[color] = btn
            color_layout.addWidget(btn)

        color_layout.addStretch()
        layout.addWidget(color_row)

        # Pre-select default color
        self.select_color(AVATAR_COLORS[0])

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(spacer)

        # Start button
        self._start_btn = QPushButton(t("welcome.start_button"))
        self._start_btn.setObjectName("start_btn")
        self._start_btn.setEnabled(False)
        self._start_btn.clicked.connect(self.accept)
        layout.addWidget(self._start_btn)

        # Wire validation
        self._name_input.textChanged.connect(self._on_name_changed)

    def _on_name_changed(self, text: str) -> None:
        self._start_btn.setEnabled(bool(text.strip()))
