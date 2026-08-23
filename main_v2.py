from __future__ import annotations

import logging
import sys
import urllib.parse
from datetime import datetime

from PyQt6.QtCore import QEvent, QObject, Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QApplication, QDialog, QHBoxLayout, QMainWindow, QWidget

from src.i18n import init_translator
from src.models.channel import Channel
from src.profiles.manager import ProfileManager
from src.services.epg_service import EpgService
from src.services.playlist_service import PlaylistService
from src.v2.dialogs.playlist_dialog import PlaylistDialog
from src.v2.nav_rail import NavRail
from src.v2.navigator import ScreenNavigator
from src.v2.screens.epg_screen import EpgScreen
from src.v2.screens.home_screen import HomeScreen
from src.v2.screens.import_screen import ImportScreen
from src.v2.screens.live_tv_screen import LiveTvScreen
from src.v2.screens.profile_screen import ProfileScreen
from src.v2.screens.search_screen import SearchScreen
from src.v2.screens.settings_screen import SettingsScreen
from src.v2.screens.vod_screen import VodScreen
from src.v2.themes import Theme, apply_theme


def _format_epg_time(raw: str) -> str:
    """Format an XMLTV timestamp like '20260101000000 +0000' into 'HH:MM'."""
    try:
        dt = datetime.strptime(raw.split(" ")[0], "%Y%m%d%H%M%S")
        return dt.strftime("%H:%M")
    except Exception:
        return ""


def _build_live_epg_data(
    channels: list[Channel], epg_service: EpgService
) -> dict[str, dict[str, str]]:
    """Build the now-playing EPG map consumed by LiveTvScreen.load_channels."""
    data: dict[str, dict[str, str]] = {}
    for ch in channels:
        if not ch.tvg_id:
            continue
        now, _nxt = epg_service.get_now_next(ch.tvg_id)
        if now is None:
            continue
        data[ch.tvg_id] = {
            "now_title": now.title,
            "start": _format_epg_time(now.start),
            "end": _format_epg_time(now.stop),
        }
    return data


def _build_xtream_playlist_url(server: str, username: str, password: str) -> str:
    """Build a Xtream Codes get.php M3U-plus URL from server/user/pass."""
    server = server.rstrip("/")
    params = {
        "username": username,
        "password": password,
        "type": "m3u_plus",
        "output": "m3u8",
    }
    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    return f"{server}/get.php?{query}"


def main() -> None:
    app = QApplication(sys.argv)

    # Translator must be initialized before any widget that calls t()
    init_translator()

    # Profile manager
    manager = ProfileManager()
    profile = manager.active_profile() if not manager.needs_welcome() else None

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
    # Render immediately; channels arrive via PlaylistService
    home.populate([], profile)

    def on_home_channel_clicked(ch: Channel) -> None:
        navigator.set_play_on_navigate(ch)
        navigator.navigate("live_tv")

    home.channel_clicked.connect(on_home_channel_clicked)

    channels: list[Channel] = []
    epg_service = EpgService()

    def _on_epg_error(message: str) -> None:
        logging.getLogger(__name__).warning("EPG error: %s", message)

    epg_service.epg_error.connect(_on_epg_error)
    live = LiveTvScreen(channels, epg_service=epg_service)
    vod = VodScreen()
    epg = EpgScreen(epg_service=epg_service)
    search = SearchScreen()
    settings = SettingsScreen()
    import_screen = ImportScreen()
    profile_screen = ProfileScreen(profiles=manager.list_profiles())

    navigator.register("home", home)
    navigator.register("live_tv", live)
    navigator.register("vod", vod)
    navigator.register("epg", epg)
    navigator.register("search", search)
    navigator.register("settings", settings)
    navigator.register("import", import_screen)
    navigator.register("profiles", profile_screen)

    # Wire auto-play from navigator to live screen
    navigator.play_requested.connect(live.play_channel)

    def _play_channel(ch: Channel) -> None:
        navigator.set_play_on_navigate(ch)
        navigator.navigate("live_tv")

    vod.channel_selected.connect(_play_channel)
    epg.channel_selected.connect(_play_channel)
    search.channel_selected.connect(_play_channel)

    settings.close_requested.connect(navigator.go_back)
    settings.import_requested.connect(lambda: navigator.navigate("import"))
    import_screen.cancelled.connect(navigator.go_back)

    def _on_profile_selected(p: object) -> None:
        from src.models.profile import Profile as _Profile
        if isinstance(p, _Profile):
            manager.switch_profile(p.id)
            navigator.navigate("home")

    profile_screen.profile_selected.connect(_on_profile_selected)
    profile_screen.add_profile_requested.connect(lambda: navigator.navigate("home"))

    # Load playlist from active profile (async for URLs, sync for files)
    playlist_service = PlaylistService()

    def _on_channels_loaded(loaded: list[Channel]) -> None:
        nonlocal channels
        channels = loaded
        home.populate(loaded, profile)
        live.load_channels(loaded, epg_data=_build_live_epg_data(loaded, epg_service))
        vod.load_channels(loaded)
        epg.load_channels(loaded)
        search.load_channels(loaded)
        if navigator.current_screen() == "import":
            import_screen.set_progress(False)
            navigator.navigate("home")

    def _on_epg_ready() -> None:
        epg.load_channels(channels)
        live.update_epg_data(_build_live_epg_data(channels, epg_service))

    def _on_playlist_error(message: str) -> None:
        if navigator.current_screen() == "import":
            import_screen.set_progress(False)
            import_screen.set_status(message)
        else:
            logging.getLogger(__name__).warning("Playlist error: %s", message)

    def _on_import_requested(payload: dict[str, str]) -> None:
        if profile is None:
            return
        method = payload.get("method")
        if method == "file":
            path = payload["path"]
            profile.playlist_path = path
            profile.playlist_url = ""
            manager.save_active()
            import_screen.set_status("")
            import_screen.set_progress(True)
            playlist_service.load_file(path)
        elif method == "url":
            url = payload["url"]
            profile.playlist_url = url
            profile.playlist_path = ""
            manager.save_active()
            import_screen.set_status("")
            import_screen.set_progress(True)
            playlist_service.load_url(url)
        elif method == "xtream":
            url = _build_xtream_playlist_url(
                payload["server"], payload["username"], payload["password"]
            )
            profile.playlist_url = url
            profile.playlist_path = ""
            manager.save_active()
            import_screen.set_status("")
            import_screen.set_progress(True)
            playlist_service.load_url(url)

    epg_service.epg_ready.connect(_on_epg_ready)

    playlist_service.channels_loaded.connect(_on_channels_loaded)
    playlist_service.fetch_error.connect(_on_playlist_error)
    import_screen.import_requested.connect(_on_import_requested)
    if profile and (profile.playlist_url or profile.playlist_path):
        home.set_loading(True)
        playlist_service.load_profile(profile)
    if profile and profile.epg_url:
        epg_service.start(profile.epg_url)

    # Handler: user clicked "Configurar lista M3U" in the empty state
    def _on_load_playlist_requested() -> None:
        dlg = PlaylistDialog(window)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            if dlg.result_url:
                profile.playlist_url = dlg.result_url
                profile.playlist_path = ""
            elif dlg.result_path:
                profile.playlist_url = ""
                profile.playlist_path = dlg.result_path
            manager.save_active()
            home.set_loading(True)
            playlist_service.load_profile(profile)

    home.load_playlist_requested.connect(_on_load_playlist_requested)

    # Global keyboard shortcuts
    class _GlobalKeyFilter(QObject):
        def __init__(self, nav: ScreenNavigator, search_widget: QObject) -> None:
            super().__init__()
            self._nav = nav
            self._search_widget = search_widget

        def eventFilter(self, obj: QObject | None, event: QEvent | None) -> bool:
            if not isinstance(event, QKeyEvent):
                return super().eventFilter(obj, event)
            if event.type() != QEvent.Type.KeyPress:
                return super().eventFilter(obj, event)
            key = event.key()
            mods = event.modifiers()
            focus = QApplication.focusWidget()
            # Don't intercept when text input is focused (except Esc)
            from PyQt6.QtWidgets import QLineEdit
            if isinstance(focus, QLineEdit) and key != Qt.Key.Key_Escape:
                return super().eventFilter(obj, event)
            if key == Qt.Key.Key_Escape:
                if focus is not self._search_widget:
                    self._nav.go_back()
                    return True
            elif key == Qt.Key.Key_H:
                self._nav.navigate("home")
                return True
            elif key == Qt.Key.Key_G:
                self._nav.navigate("epg")
                return True
            elif key == Qt.Key.Key_V:
                self._nav.navigate("vod")
                return True
            elif key == Qt.Key.Key_L:
                self._nav.navigate("live_tv")
                return True
            elif key == Qt.Key.Key_Slash or (
                key == Qt.Key.Key_F
                and mods == Qt.KeyboardModifier.ControlModifier
            ):
                self._nav.navigate("search")
                return True
            return super().eventFilter(obj, event)

    app.installEventFilter(_GlobalKeyFilter(navigator, live._search))

    # Main window
    window = QMainWindow()
    window.setWindowTitle("Libre IPTV v2")

    nav_rail = NavRail(profile=profile)
    nav_rail.navigate_requested.connect(navigator.navigate)
    navigator.screen_changed.connect(nav_rail.set_active)

    shell = QWidget()
    shell_layout = QHBoxLayout(shell)
    shell_layout.setContentsMargins(0, 0, 0, 0)
    shell_layout.setSpacing(0)
    shell_layout.addWidget(nav_rail)
    shell_layout.addWidget(navigator, stretch=1)

    window.setCentralWidget(shell)
    window.resize(1280, 720)

    # Restore last screen
    navigator.restore_last_screen()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
