from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget


class ToastNotification(QFrame):
    closed = pyqtSignal()

    def __init__(
        self,
        message: str,
        kind: str,
        duration_ms: int,
        parent: QWidget,
    ) -> None:
        super().__init__(parent)
        self._kind = kind
        self._duration_ms = duration_ms

        self.setObjectName("toast")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)

        if kind == "success":
            self.setStyleSheet(
                "#toast { background-color: #4caf50; color: #ffffff; "
                "border-radius: 6px; padding: 8px 16px; }"
            )
        elif kind == "error":
            self.setStyleSheet(
                "#toast { background-color: #f44336; color: #ffffff; "
                "border-radius: 6px; padding: 8px 16px; }"
            )
        else:
            self.setStyleSheet(
                "#toast { background-color: #37474f; color: #ffffff; "
                "border-radius: 6px; padding: 8px 16px; }"
            )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        self._message_label = QLabel(message)
        self._message_label.setStyleSheet("color: #ffffff; background: transparent;")
        layout.addWidget(self._message_label)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._dismiss)

    def show(self) -> None:
        super().show()
        self._timer.start(self._duration_ms)

    def _dismiss(self) -> None:
        self.closed.emit()
        self.deleteLater()


class ToastManager:
    def __init__(self, parent: QWidget) -> None:
        self._parent = parent
        self._toasts: list[ToastNotification] = []

    def show(self, message: str, kind: str, duration_ms: int = 3000) -> None:
        toast = ToastNotification(message, kind, duration_ms, self._parent)
        toast.closed.connect(lambda t=toast: self._remove_toast(t))
        self._toasts.append(toast)
        self._reposition()
        toast.show()

    def _remove_toast(self, toast: ToastNotification) -> None:
        if toast in self._toasts:
            self._toasts.remove(toast)
        self._reposition()

    def _reposition(self) -> None:
        parent_rect = self._parent.rect()
        margin = 16
        x = parent_rect.width() - 300 - margin
        y = parent_rect.height() - margin
        for toast in reversed(self._toasts):
            toast.move(x, y - toast.height())
            y -= toast.height() + 4
