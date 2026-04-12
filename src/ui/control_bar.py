from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSlider, QWidget


class ControlBarWidget(QWidget):
    volume_changed = pyqtSignal(int)
    mute_toggled = pyqtSignal(bool)
    stop_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._muted = False
        self.setStyleSheet(
            "ControlBarWidget { background: #1e1e1e; border-top: 1px solid #3a3a3a; }"
            "QPushButton { background: #2d2d2d; color: #e0e0e0; "
            "border: 1px solid #3a3a3a; border-radius: 4px; padding: 4px 12px; }"
            "QPushButton:hover { background: #3a3a3a; }"
            "QPushButton:pressed { background: #0d6efd; }"
        )

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.setFixedWidth(120)

        self.mute_btn = QPushButton("🔇 Mute")
        self.stop_btn = QPushButton("■ Stop")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.addWidget(QLabel("Vol:"))
        layout.addWidget(self.volume_slider)
        layout.addWidget(self.mute_btn)
        layout.addWidget(self.stop_btn)
        layout.addStretch()

        self.volume_slider.valueChanged.connect(self.volume_changed.emit)
        self.mute_btn.clicked.connect(self._on_mute_clicked)
        self.stop_btn.clicked.connect(self.stop_requested.emit)
        self.setFixedHeight(48)

    def _on_mute_clicked(self) -> None:
        self._muted = not self._muted
        self.mute_btn.setText("🔊 Unmute" if self._muted else "🔇 Mute")
        self.mute_toggled.emit(self._muted)
