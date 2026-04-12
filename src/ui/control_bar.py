from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSlider, QWidget


class ControlBarWidget(QWidget):
    volume_changed = pyqtSignal(int)
    mute_toggled = pyqtSignal(bool)
    stop_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._muted = False

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.setFixedWidth(120)

        self.mute_btn = QPushButton("Mute")
        self.stop_btn = QPushButton("Stop")

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
        self.mute_btn.setText("Unmute" if self._muted else "Mute")
        self.mute_toggled.emit(self._muted)
