from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent, QKeyEvent
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QInputDialog,
    QMainWindow,
    QMenuBar,
    QSplitter,
    QStatusBar,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from src.core.parental import get_blocked_sets
from src.core.vlc_manager import VlcManager
from src.i18n import get_translator, t
from src.models.channel import Channel
from src.models.profile import Profile
from src.profiles.manager import ProfileManager
from src.services.epg_service import EpgService
from src.services.menu_builder import MenuBuilder
from src.services.playlist_service import PlaylistService
from src.services.profile_controller import ProfileController
from src.ui.app_settings import AppSettings
from src.ui.channel_list import ChannelListPanel, _EpgInfo
from src.ui.control_bar import ControlBarWidget
from src.ui.grid_player_widget import GridPlayerWidget
from src.ui.loading_overlay import LoadingOverlay
from src.ui.parental_panel import ParentalControlsPanel
from src.ui.pin_dialog import PinDialog
from src.ui.profile_bar import ProfileSelectorBar
from src.ui.toast import ToastManager

_DEFAULT_LEFT_WIDTH = 280


class MainWindow(QMainWindow):
    def __init__(
        self,
        manager: ProfileManager | None = None,
        menu_builder: MenuBuilder | None = None,
        playlist_service: PlaylistService | None = None,
        profile_controller: ProfileController | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._manager = manager

        self._playlist_service = playlist_service or PlaylistService(self)
        self._profile_controller = profile_controller or (
            ProfileController(manager, self) if manager is not None else None
        )
        self._menu_builder = menu_builder or MenuBuilder()

        self.setWindowTitle(t("app.title"))
        self.setMinimumSize(900, 600)

        self._channel_list_panel = ChannelListPanel(manager=manager)
        self._channel_list = self._channel_list_panel.channel_list
        self._grid = GridPlayerWidget()
        self._control_bar = ControlBarWidget()
        self._epg_service = EpgService(parent=self)
        self._epg_service.epg_ready.connect(self._on_epg_ready)
        self._epg_service.epg_error.connect(self._on_epg_error)

        # Left panel: profile bar (if manager) + channel list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        if manager is not None:
            self._profile_bar = ProfileSelectorBar(manager)
            self._profile_bar.profile_switched.connect(self._on_profile_switched)
            left_layout.addWidget(self._profile_bar)
        left_layout.addWidget(self._channel_list_panel)

        self._loading_overlay = LoadingOverlay(left_panel)

        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.addWidget(self._grid, stretch=1)
        right_layout.addWidget(self._control_bar)

        left_panel.setMinimumWidth(_DEFAULT_LEFT_WIDTH // 2)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_container)
        splitter.setSizes([_DEFAULT_LEFT_WIDTH, 620])
        splitter.setCollapsible(0, False)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet("QSplitter::handle { background: #3a3a3a; }")
        splitter.splitterMoved.connect(self._on_splitter_moved)
        self._splitter = splitter

        # Wire control bar to always route through the active player
        self._control_bar.volume_changed.connect(
            lambda v: self._grid.active_player().set_volume(v)
        )
        self._control_bar.stop_requested.connect(self._grid.stop_active)
        self._control_bar.mute_toggled.connect(
            lambda _: self._grid.active_player().toggle_mute()
        )

        self.setCentralWidget(splitter)
        self._toast_manager = ToastManager(splitter)

        status_bar = QStatusBar()
        status_bar.setStyleSheet(
            "QStatusBar { background: #1a1a1a; color: #888888; "
            "border-top: 1px solid #3a3a3a; }"
        )
        self.setStatusBar(status_bar)
        status_bar.showMessage(t("app.status.no_playlist"))

        # Wire services
        self._playlist_service.channels_loaded.connect(self._on_fetch_complete)
        self._playlist_service.fetch_error.connect(self._on_fetch_error)
        self._playlist_service.status_message.connect(self._on_status_message)

        if self._profile_controller is not None:
            self._profile_controller.profile_changed.connect(self._on_profile_changed)
            self._profile_controller.favorites_changed.connect(self._on_favorites_changed)

        # Build menus via MenuBuilder
        menu_bar = self._menu_builder.build({
            "open_playlist": self._open_playlist,
            "open_url": self._open_url,
            "quit": QApplication.quit,
            "stop": self._grid.stop_active,
            "layout_single": lambda: self._grid.set_mode(1),
            "layout_dual": lambda: self._grid.set_mode(2),
            "layout_quad": lambda: self._grid.set_mode(4),
            "about": self._show_about_dialog,
        })
        self.setMenuBar(menu_bar)
        self._extract_menu_references(menu_bar)
        self._build_layout_toolbar()

        self._channel_list.channel_selected.connect(self._on_channel_selected)
        self._channel_list.favorite_toggled.connect(self._on_favorite_toggled)
        self._grid.active_cell_changed.connect(self._on_active_cell_changed)

        self._channels: list[Channel] = []
        self._fullscreen: bool = False
        self._normal_splitter_sizes: list[int] = [_DEFAULT_LEFT_WIDTH, 620]
        self._settings = AppSettings()
        self._restore_settings()

        if manager is not None:
            self._auto_load_profile(manager.active_profile())

        tr = get_translator()
        if tr is not None:
            tr.language_changed.connect(self._retranslate)

    def _extract_menu_references(self, menu_bar: QMenuBar) -> None:
        """Capture references to menus/actions built by MenuBuilder."""
        self._file_menu = None
        self._open_file_action = None
        self._open_url_action = None
        self._quit_action = None
        self._playback_menu = None
        self._stop_action = None
        self._view_menu = None
        self._layout_menu = None
        self._help_menu = None
        self._about_action = None

        for action in menu_bar.actions():
            menu = action.menu()
            if menu is None:
                continue
            text = action.text()
            if text == t("menu.file"):
                self._file_menu = menu
                for a in menu.actions():
                    at = a.text()
                    if at == t("menu.open_playlist"):
                        self._open_file_action = a
                    elif at == t("menu.open_url"):
                        self._open_url_action = a
                    elif at == t("menu.quit"):
                        self._quit_action = a
            elif text == t("menu.playback"):
                self._playback_menu = menu
                for a in menu.actions():
                    if a.text() == t("menu.stop"):
                        self._stop_action = a
            elif text == t("menu.view"):
                self._view_menu = menu
                for a in menu.actions():
                    if a.text() == t("layout.toolbar"):
                        self._layout_menu = a.menu()
            elif text == t("menu.help"):
                self._help_menu = menu
                for a in menu.actions():
                    if a.text() == t("menu.about"):
                        self._about_action = a

        # Add settings menu directly in MainWindow (not part of MenuBuilder)
        self._settings_menu = menu_bar.addMenu(t("menu.settings"))
        assert self._settings_menu is not None
        self._parental_action = self._settings_menu.addAction(
            t("parental.action"), self._show_parental_controls
        )

    def _build_layout_toolbar(self) -> None:
        toolbar = QToolBar(t("layout.toolbar"))
        toolbar.setMovable(False)
        toolbar.setObjectName("layout_toolbar")
        toolbar.setStyleSheet(
            "QToolBar { background: #0d0d0d;"
            " border-bottom: 1px solid #1e1e1e;"
            " spacing: 4px; padding: 4px 8px; }"
            "QToolButton { background: #1e1e1e; color: #9e9e9e;"
            " border: 1px solid #2a2a2a; border-radius: 6px;"
            " padding: 4px 14px; font-size: 13px; }"
            "QToolButton:hover { background: #262626; color: #e0e0e0; }"
            "QToolButton:checked { background: #00bcd4;"
            " color: #000000; border-color: #00bcd4; }"
        )

        self._layout_buttons: dict[int, QToolButton] = {}
        _modes = [
            (1, "⬜  1", t("layout.single_tooltip")),
            (2, "⬛  2", t("layout.dual_tooltip")),
            (4, "▦  4", t("layout.quad_tooltip")),
        ]
        for mode, label, tip in _modes:
            btn = QToolButton()
            btn.setText(label)
            btn.setToolTip(tip)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, m=mode: self._set_layout_mode(m))
            toolbar.addWidget(btn)
            self._layout_buttons[mode] = btn

        self._layout_buttons[1].setChecked(True)
        self.addToolBar(toolbar)

    def _set_layout_mode(self, mode: int) -> None:
        self._grid.set_mode(mode)
        for m, btn in self._layout_buttons.items():
            btn.setChecked(m == mode)

    def _retranslate(self, _code: str) -> None:
        self.setWindowTitle(t("app.title"))
        sb = self.statusBar()
        if sb:
            sb.showMessage(t("app.status.no_playlist"))

        if self._file_menu is not None:
            self._file_menu.setTitle(t("menu.file"))
        if self._open_file_action is not None:
            self._open_file_action.setText(t("menu.open_playlist"))
        if self._open_url_action is not None:
            self._open_url_action.setText(t("menu.open_url"))
        if self._quit_action is not None:
            self._quit_action.setText(t("menu.quit"))

        if self._playback_menu is not None:
            self._playback_menu.setTitle(t("menu.playback"))
        if self._stop_action is not None:
            self._stop_action.setText(t("menu.stop"))

        if self._view_menu is not None:
            self._view_menu.setTitle(t("menu.view"))
        if self._layout_menu is not None:
            self._layout_menu.setTitle(t("layout.toolbar"))

        if self._help_menu is not None:
            self._help_menu.setTitle(t("menu.help"))
        if self._about_action is not None:
            self._about_action.setText(t("menu.about"))

        if self._settings_menu is not None:
            self._settings_menu.setTitle(t("menu.settings"))
        if self._parental_action is not None:
            self._parental_action.setText(t("parental.action"))

        _tooltips = {
            1: t("layout.single_tooltip"),
            2: t("layout.dual_tooltip"),
            4: t("layout.quad_tooltip"),
        }
        for mode, btn in self._layout_buttons.items():
            btn.setToolTip(_tooltips[mode])

    def _fetch_start(self, text: str = "") -> None:
        if self._open_file_action is not None:
            self._open_file_action.setEnabled(False)
        if self._open_url_action is not None:
            self._open_url_action.setEnabled(False)
        parent = self._loading_overlay.parentWidget()
        assert parent is not None
        self._loading_overlay.setGeometry(parent.rect())
        self._loading_overlay.show_loading(text or t("loading.default_text"))

    def _fetch_end(self) -> None:
        if self._open_file_action is not None:
            self._open_file_action.setEnabled(True)
        if self._open_url_action is not None:
            self._open_url_action.setEnabled(True)
        self._loading_overlay.hide_loading()

    def _auto_load_profile(self, profile: Profile) -> None:
        """Load playlist for the given profile if one is configured."""
        self._playlist_service.load_profile(profile)
        self._epg_service.start(profile.epg_url)

    def _build_epg_data(self) -> dict[str, _EpgInfo]:
        """Build EPG info map for current channels."""
        data: dict[str, _EpgInfo] = {}
        for ch in self._channels:
            if ch.tvg_id:
                now, nxt = self._epg_service.get_now_next(ch.tvg_id)
                data[ch.tvg_id] = _EpgInfo(
                    now_title=now.title if now else "",
                    next_title=nxt.title if nxt else "",
                )
        return data

    def _reload_channel_list(self) -> None:
        """Reload channel list with profile favorites, recent, blocks, and EPG."""
        favorites: list[str] = []
        recent: list[str] = []
        blocked_urls: frozenset[str] = frozenset()
        blocked_groups: frozenset[str] = frozenset()
        epg_data: dict[str, _EpgInfo] = {}
        if self._manager is not None:
            profile = self._manager.active_profile()
            favorites = profile.favorites
            recent = profile.recent
            blocked_urls, blocked_groups = get_blocked_sets(profile)
        epg_data = self._build_epg_data()
        self._channel_list.load_channels(
            self._channels,
            favorites=favorites,
            recent=recent,
            blocked_urls=blocked_urls,
            blocked_groups=blocked_groups,
            epg_data=epg_data,
        )

    def _on_profile_switched(self, profile: Profile) -> None:
        """Handle profile switch: delegate to ProfileController."""
        if self._profile_controller is not None:
            self._profile_controller.switch_profile(profile.id)

    def _on_profile_changed(self, profile: Profile) -> None:
        """React to profile change: stop playback, clear list, auto-load."""
        self._grid.stop_active()
        self._channels = []
        self._channel_list.load_channels([])
        self._epg_service.stop()
        self._auto_load_profile(profile)
        if hasattr(self, "_profile_bar"):
            self._profile_bar.refresh()

    def _on_favorites_changed(self) -> None:
        """Refresh channel list when favorites change."""
        if self._profile_controller is not None:
            self._channel_list.reload_with_profile(self._profile_controller.active_profile())

    def _on_epg_ready(self) -> None:
        """Refresh channel list and status bar when EPG data is ready."""
        self._reload_channel_list()
        player = self._grid.active_player()
        current_url = getattr(player, "_current_url", "")
        for ch in self._channels:
            if ch.url == current_url:
                self._update_status_bar_with_epg(ch)
                break

    def _on_epg_error(self, message: str) -> None:
        """Log EPG error and continue without data."""
        import logging
        logging.getLogger(__name__).warning("EPG error: %s", message)

    def _update_status_bar_with_epg(self, channel: Channel) -> None:
        """Update status bar with current programme info for the channel."""
        sb = self.statusBar()
        assert sb is not None
        if not channel.tvg_id:
            sb.showMessage(channel.name)
            return
        now, _nxt = self._epg_service.get_now_next(channel.tvg_id)
        if now:
            sb.showMessage(f"{channel.name} — {now.title} ({now.start} - {now.stop})")
        else:
            sb.showMessage(channel.name)

    def _on_splitter_moved(self, pos: int, index: int) -> None:  # noqa: ARG002
        if not self._fullscreen:
            self._normal_splitter_sizes = self._splitter.sizes()

    def _restore_settings(self) -> None:
        geometry = self._settings.load_geometry()
        if geometry is not None:
            self.restoreGeometry(geometry)
        sizes = self._settings.load_splitter()
        if sizes is not None and len(sizes) == 2 and all(s > 0 for s in sizes):
            self._normal_splitter_sizes = sizes
            self._splitter.setSizes(sizes)

    def closeEvent(self, event: QCloseEvent | None) -> None:
        self._settings.save_geometry(self.saveGeometry())
        # Never save splitter sizes from fullscreen — the left panel is hidden
        # and sizes would be [0, X], breaking the next session.
        self._settings.save_splitter(self._normal_splitter_sizes)
        if self._manager is not None:
            self._manager.save_active()
        VlcManager.release()
        super().closeEvent(event)

    def keyPressEvent(self, event: QKeyEvent | None) -> None:
        if event is None:
            return
        key = event.key()
        text = event.text()

        if key == Qt.Key.Key_F11 or (key == Qt.Key.Key_F and not text):
            self._toggle_fullscreen()
        elif key == Qt.Key.Key_Escape and self._fullscreen:
            self._fullscreen = False
            self.showNormal()
        elif text == "1":
            self._set_layout_mode(1)
        elif text == "2":
            self._set_layout_mode(2)
        elif text == "4":
            self._set_layout_mode(4)
        elif key == Qt.Key.Key_M:
            self._grid.active_player().toggle_mute()
        elif key == Qt.Key.Key_Space:
            self._grid.stop_active()
        else:
            super().keyPressEvent(event)

    def _toggle_fullscreen(self) -> None:
        if self._fullscreen:
            self._fullscreen = False
            # Restore all hidden panels
            for toolbar in self.findChildren(QToolBar):
                toolbar.show()
            sb = self.statusBar()
            if sb:
                sb.show()
            panel = self._splitter.widget(0)
            if panel:
                panel.show()
            self.showNormal()
        else:
            self._fullscreen = True
            # Hide everything except the video grid
            for toolbar in self.findChildren(QToolBar):
                toolbar.hide()
            sb = self.statusBar()
            if sb:
                sb.hide()
            panel = self._splitter.widget(0)
            if panel:
                panel.hide()
            self.showFullScreen()

    def _show_about_dialog(self) -> None:
        from src.ui.about_dialog import AboutDialog

        dialog = AboutDialog(parent=self)
        dialog.exec()

    def _show_parental_controls(self) -> None:
        if self._manager is None:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle(t("parental.dialog_title"))
        dialog.setMinimumSize(400, 500)
        dialog.setStyleSheet("QDialog { background: #161616; }")
        layout = QVBoxLayout(dialog)
        panel = ParentalControlsPanel(
            manager=self._manager, channels=self._channels, parent=dialog
        )
        panel.pin_changed.connect(self._reload_channel_list)
        panel.blocks_changed.connect(self._reload_channel_list)
        layout.addWidget(panel)
        dialog.exec()

    def _open_playlist(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            t("dialog.open_playlist_title"),
            "",
            t("dialog.playlist_filter"),
        )
        if not path:
            return
        if self._manager is not None:
            self._manager.update_playlist(path=path)
            self._manager.save_active()
        self._settings.save_last_playlist(path)
        self._playlist_service.load_file(path)

    def _open_url(self) -> None:
        url, ok = QInputDialog.getText(
            self, t("dialog.open_url_title"), t("dialog.open_url_label")
        )
        if not ok or not url.strip():
            return
        if self._manager is not None:
            self._manager.update_playlist(url=url.strip())
            self._manager.save_active()
        self._fetch_start()
        self._playlist_service.load_url(url.strip())

    def _on_fetch_complete(self, channels: list[Channel]) -> None:
        self._fetch_end()
        self._channels = channels
        self._reload_channel_list()
        status_bar = self.statusBar()
        assert status_bar is not None
        status_bar.showMessage(t("app.status.channels_loaded", count=len(channels)))
        self._toast_manager.show(t("app.toast.channels_loaded"), "success", 3000)

    def _on_favorite_toggled(self, channel_url: str) -> None:
        if self._profile_controller is None:
            return
        self._profile_controller.toggle_favorite(channel_url)

    def _on_fetch_error(self, message: str) -> None:
        self._fetch_end()
        status_bar = self.statusBar()
        assert status_bar is not None
        status_bar.showMessage(t("app.status.error", message=message))
        self._toast_manager.show(
            t("app.toast.channels_load_error", message=message), "error", 5000
        )

    def _on_status_message(self, message: str) -> None:
        status_bar = self.statusBar()
        if status_bar is not None:
            status_bar.showMessage(message)

    def _on_active_cell_changed(self, index: int) -> None:  # noqa: ARG002
        volume = self._grid.active_player().get_volume()
        self._control_bar.volume_slider.blockSignals(True)
        self._control_bar.volume_slider.setValue(volume)
        self._control_bar.volume_slider.blockSignals(False)

    def _on_channel_selected(self, channel: Channel) -> None:
        if self._manager is not None and self._manager.is_channel_blocked(channel):
            dialog = PinDialog(parent=self)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            entered = dialog.pin_value()
            if not entered or not self._manager.verify_pin(entered):
                self._toast_manager.show(
                    t("parental.error.incorrect_pin"), "error", 3000
                )
                return
        self._grid.play_in_active(channel.url)
        if self._profile_controller is not None:
            self._profile_controller.add_to_recent(channel.url)
        self._update_status_bar_with_epg(channel)
