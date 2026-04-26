from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSlider, QWidget

from src.i18n import get_translator, t

_ACCENT = "#00bcd4"
_SURFACE = "#1a1a1a"
_ELEVATED = "#262626"
_BORDER = "#2a2a2a"
_TEXT = "#e0e0e0"


class ControlBarWidget(QWidget):
    volume_changed = pyqtSignal(int)
    mute_toggled = pyqtSignal(bool)
    stop_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._muted = False
        _qss = (
            f"ControlBarWidget {{ background: {_SURFACE};"
            f" border-top: 1px solid {_BORDER}; }}"
            f"QPushButton {{ background: {_ELEVATED}; color: {_TEXT};"
            f" border: 1px solid {_BORDER}; border-radius: 6px;"
            f" padding: 6px 16px; font-size: 13px; }}"
            f"QPushButton:hover {{ background: #333333;"
            f" border-color: {_ACCENT}; }}"
            f"QPushButton:pressed {{ background: {_ACCENT}; color: #000000; }}"
            "QSlider::groove:horizontal { height: 4px;"
            " background: #2a2a2a; border-radius: 2px; }"
            f"QSlider::sub-page:horizontal {{ background: {_ACCENT};"
            " border-radius: 2px; }"
            "QSlider::handle:horizontal { width: 14px; height: 14px;"
            " margin: -5px 0; border-radius: 7px; background: #ffffff; }"
        )
        self.setStyleSheet(_qss)

        vol_icon = QLabel("🔊")
        vol_icon.setStyleSheet(f"color: {_TEXT}; font-size: 16px; padding: 0 4px;")

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.setFixedWidth(160)
        self.volume_slider.setToolTip(t("control.volume_tooltip"))

        self.mute_btn = QPushButton(t("control.mute"))
        self.stop_btn = QPushButton(t("control.stop"))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)
        layout.addWidget(vol_icon)
        layout.addWidget(self.volume_slider)
        layout.addSpacing(8)
        layout.addWidget(self.mute_btn)
        layout.addWidget(self.stop_btn)
        layout.addStretch()

        self.volume_slider.valueChanged.connect(self.volume_changed.emit)
        self.mute_btn.clicked.connect(self._on_mute_clicked)
        self.stop_btn.clicked.connect(self.stop_requested.emit)
        self.setFixedHeight(56)

        tr = get_translator()
        if tr is not None:
            tr.language_changed.connect(self._retranslate)

    def _retranslate(self, _code: str) -> None:
        self.volume_slider.setToolTip(t("control.volume_tooltip"))
        self.stop_btn.setText(t("control.stop"))
        self._update_mute_text()

    def _update_mute_text(self) -> None:
        self.mute_btn.setText(
            t("control.unmute") if self._muted else t("control.mute")
        )

    def _on_mute_clicked(self) -> None:
        self._muted = not self._muted
        self._update_mute_text()
        self.mute_toggled.emit(self._muted)
