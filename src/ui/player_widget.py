import vlc
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QMouseEvent, QShowEvent  # noqa: F401
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

import src.platform as platform
from src.i18n import t


class PlayerWidget(QFrame):
    clicked = pyqtSignal()

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        vlc_instance: vlc.Instance | None = None,
    ) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: black;")
        self._owns_instance = vlc_instance is None
        self._vlc_instance = (
            vlc_instance if vlc_instance is not None else vlc.Instance()
        )
        self._media_player = self._vlc_instance.media_player_new()
        self._hwnd_bound = False
        self._placeholder_shown = True

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._placeholder = QLabel(t("player.placeholder"), self)
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setStyleSheet("color: #888888; background: transparent;")
        layout.addWidget(self._placeholder)

    def showEvent(self, event: QShowEvent | None) -> None:
        super().showEvent(event)
        if not self._hwnd_bound:
            QTimer.singleShot(0, self._bind_vlc)

    def _bind_vlc(self) -> None:
        platform.bind_vlc(self._media_player, int(self.winId()))
        self._hwnd_bound = True

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        self.clicked.emit()
        super().mousePressEvent(event)

    def set_active(self, active: bool) -> None:
        if active:
            self.setStyleSheet(
                "background-color: black; border: 2px solid #00bcd4;"
            )
        else:
            self.setStyleSheet("background-color: black;")

    def play(self, url: str) -> None:
        if self._placeholder_shown:
            self._placeholder.hide()
            self._placeholder_shown = False
        if not self._hwnd_bound:
            self._bind_vlc()
        media = self._vlc_instance.media_new(url)
        self._media_player.set_media(media)
        self._media_player.play()

    def stop(self) -> None:
        self._media_player.stop()

    def set_volume(self, volume: int) -> None:
        self._media_player.audio_set_volume(volume)

    def get_volume(self) -> int:
        vol = self._media_player.audio_get_volume()
        return 100 if vol == -1 else vol

    def toggle_mute(self) -> bool:
        self._media_player.audio_toggle_mute()
        result = self._media_player.audio_get_mute()
        return bool(result)

    def closeEvent(self, event: QCloseEvent | None) -> None:
        self._media_player.release()
        if self._owns_instance:
            self._vlc_instance.release()
        super().closeEvent(event)
