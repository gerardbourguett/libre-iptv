from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter, QPaintEvent, QPen
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.i18n import t


class LoadingOverlay(QWidget):
    """Semi-transparent overlay with an animated arc spinner."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 180);")

        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self._timer.setInterval(33)  # ~30 fps

        self._label = QLabel(t("loading.default_text"), self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self._label.setStyleSheet("color: #e0e0e0; background: transparent;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(self._label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        self.hide()

    def show_loading(self, text: str = "") -> None:
        self._label.setText(text or t("loading.default_text"))
        self.show()
        self.raise_()
        self._timer.start()

    def hide_loading(self) -> None:
        self._timer.stop()
        self.hide()

    def _rotate(self) -> None:
        self._angle = (self._angle + 10) % 360
        self.update()

    def paintEvent(self, event: QPaintEvent | None) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(QColor("#00bcd4"))
        pen.setWidth(4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        rect = self.rect().adjusted(20, 20, -20, -20)
        center = rect.center()
        size = min(rect.width(), rect.height())
        cx = center.x() - size // 4
        cy = center.y() - size // 4
        sz = size // 2
        spinner_rect = (cx, cy, sz, sz)

        painter.drawArc(*spinner_rect, self._angle * 16, 120 * 16)
        painter.end()
