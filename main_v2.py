from __future__ import annotations

import sys

from PyQt6.QtCore import QEvent, QObject, Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QApplication, QMainWindow

from src.i18n import init_translator
from src.models.channel import Channel
from src.profiles.manager import ProfileManager
from src.services.playlist_service import PlaylistService
from src.v2.navigator import ScreenNavigator
from src.v2.screens.home_screen import HomeScreen
from src.v2.screens.live_tv_screen import LiveTvScreen
from src.v2.themes import Theme, apply_theme


def main() -> None:
    app = QApplication(sys.argv)

    # Translator must be initialized before any widget that calls t()
    init_translator()

    # Profile manager
    manager = ProfileManager()
    profile = manager.active_profile()

    # Theme
    theme_name = profile.prefs.theme if profile else "midnight"
    theme_map = {
        "midnight": Theme.MIDNIGHT,
        "ocean": Theme.OCEAN,
        "ember": Theme.EMBER,
        "abyss": Theme.ABYSS,
        "medianoche": Theme.MIDNIGHT,
        "océano": Theme.OCEAN,
        "brasas": Theme.EMBER,
        "abismo": Theme.ABYSS,
    }
    theme = theme_map.get(theme_name, Theme.MIDNIGHT)
    apply_theme(theme, app)

    # Wire persistence via subclass to avoid method-assign mypy error
    class _PersistentNavigator(ScreenNavigator):
        def _save_last_screen(self, name: str) -> None:
            if profile:
                profile.prefs.last_screen = name
                manager.save_active()

        def _load_last_screen(self) -> str:
            return profile.prefs.last_screen if profile else "home"

    # Navigator
    navigator = _PersistentNavigator()

    # Screens
    home = HomeScreen()
    home.populate([], profile)  # Render immediately; channels arrive via PlaylistService

    def on_home_channel_clicked(ch: Channel) -> None:
        navigator.set_play_on_navigate(ch)
        navigator.navigate("live_tv")

    home.channel_clicked.connect(on_home_channel_clicked)

    channels: list[Channel] = []
    live = LiveTvScreen(channels)

    navigator.register("home", home)
    navigator.register("live_tv", live)

    # Wire auto-play from navigator to live screen
    navigator.play_requested.connect(live.play_channel)

    # Load playlist from active profile (async for URLs, sync for files)
    playlist_service = PlaylistService()

    def _on_channels_loaded(loaded: list[Channel]) -> None:
        home.populate(loaded, profile)
        live.load_channels(loaded)

    playlist_service.channels_loaded.connect(_on_channels_loaded)
    if profile:
        playlist_service.load_profile(profile)

    # Global Esc handler for back navigation (skip when search field focused)
    class _EscBackFilter(QObject):
        def __init__(self, navigator: ScreenNavigator, search_widget: QObject) -> None:
            super().__init__()
            self._navigator = navigator
            self._search_widget = search_widget

        def eventFilter(self, obj: QObject | None, event: QEvent | None) -> bool:
            if isinstance(event, QKeyEvent) and event.key() == Qt.Key.Key_Escape:
                focus = QApplication.focusWidget()
                if focus is not self._search_widget:
                    self._navigator.go_back()
                    return True
            return super().eventFilter(obj, event)

    app.installEventFilter(_EscBackFilter(navigator, live._search))

    # Main window
    window = QMainWindow()
    window.setWindowTitle("Libre IPTV v2")
    window.setCentralWidget(navigator)
    window.resize(1280, 720)

    # Restore last screen
    navigator.restore_last_screen()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
