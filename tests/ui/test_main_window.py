from unittest.mock import MagicMock, patch

import pytest

from src.models.channel import Channel
from src.ui.main_window import MainWindow


@pytest.fixture
def mock_vlc():
    with patch("src.ui.player_widget.vlc") as mock:
        instance = MagicMock()
        player = MagicMock()
        mock.Instance.return_value = instance
        instance.media_player_new.return_value = player
        yield mock, player


@pytest.fixture
def window(qtbot, mock_vlc):
    w = MainWindow()
    qtbot.addWidget(w)
    return w


class TestMainWindowLayout:
    def test_window_title_is_iptv_player(self, window):
        """S1: window title is 'IPTV Player'."""
        assert window.windowTitle() == "IPTV Player"

    def test_status_bar_default_message(self, window):
        """S4: default status bar message is 'No playlist loaded'."""
        assert window.statusBar().currentMessage() == "No playlist loaded"


class TestMenuBar:
    def _find_menu(self, window, title: str):
        for action in window.menuBar().actions():
            if action.text() == title:
                return action.menu()
        return None

    def _find_action(self, menu, title: str):
        for action in menu.actions():
            if action.text() == title:
                return action
        return None

    def test_file_menu_exists(self, window):
        """S2: File menu present in menu bar."""
        menu = self._find_menu(window, "File")
        assert menu is not None

    def test_file_menu_has_open_playlist(self, window):
        """S2: File menu contains 'Open Playlist'."""
        menu = self._find_menu(window, "File")
        action = self._find_action(menu, "Open Playlist")
        assert action is not None

    def test_file_menu_has_quit(self, window):
        """S2: File menu contains 'Quit'."""
        menu = self._find_menu(window, "File")
        action = self._find_action(menu, "Quit")
        assert action is not None

    def test_playback_menu_has_stop(self, window):
        """S3: Playback menu contains 'Stop'."""
        menu = self._find_menu(window, "Playback")
        assert menu is not None
        action = self._find_action(menu, "Stop")
        assert action is not None


class TestSignalWiring:
    def test_channel_selection_updates_status_bar(self, window, qtbot, mock_vlc):
        """S5: selecting a channel updates the status bar with channel name."""
        ch = Channel(url="http://cnn.com", name="CNN International", group="News")
        window._channel_list.channel_selected.emit(ch)
        assert window.statusBar().currentMessage() == "CNN International"


class TestOpenUrl:
    def test_open_url_action_exists_in_file_menu(self, window):
        menu_bar = window.menuBar()
        file_menu = None
        for action in menu_bar.actions():
            if action.text() == "File":
                file_menu = action.menu()
                break
        assert file_menu is not None
        action_texts = [a.text() for a in file_menu.actions()]
        assert "Open URL..." in action_texts

    def test_open_url_empty_input_does_nothing(self, window, monkeypatch):
        monkeypatch.setattr(
            "src.ui.main_window.QInputDialog.getText",
            lambda *a, **kw: ("", False)
        )
        # Should not raise
        window._open_url()
        status = window.statusBar()
        assert status is not None
        # Status unchanged from initial
        assert status.currentMessage() == "No playlist loaded"

    def test_on_fetch_complete_loads_channels_and_updates_status(self, window):
        from src.models.channel import Channel
        channels = [Channel(url="http://a.com", name="Ch1", group="")]
        window._on_fetch_complete(channels)
        assert window._channel_list.count() > 0
        status = window.statusBar()
        assert status is not None
        assert status.currentMessage() == "1 channels loaded"

    def test_on_fetch_error_shows_error_in_status(self, window):
        window._on_fetch_error("Connection refused")
        status = window.statusBar()
        assert status is not None
        assert "Connection refused" in status.currentMessage()

    def test_open_url_shows_fetching_status(self, window, monkeypatch):
        """Status bar shows 'Fetching...' while download is in progress."""
        from unittest.mock import patch

        monkeypatch.setattr(
            "src.ui.main_window.QInputDialog.getText",
            lambda *a, **kw: ("http://example.com/playlist.m3u", True),
        )
        # Patch PlaylistFetchWorker.start so it never actually runs
        with patch("src.ui.main_window.PlaylistFetchWorker.start"):
            window._open_url()

        status = window.statusBar()
        assert status is not None
        assert status.currentMessage() == "Fetching..."


class TestSettingsIntegration:
    def test_close_event_saves_geometry(self, window, monkeypatch):
        mock_settings = MagicMock()
        window._settings = mock_settings
        from PyQt6.QtGui import QCloseEvent
        event = QCloseEvent()
        window.closeEvent(event)
        mock_settings.save_geometry.assert_called_once()

    def test_close_event_saves_splitter(self, window, monkeypatch):
        mock_settings = MagicMock()
        window._settings = mock_settings
        from PyQt6.QtGui import QCloseEvent
        event = QCloseEvent()
        window.closeEvent(event)
        mock_settings.save_splitter.assert_called_once()

    def test_init_restores_splitter_if_available(self, mock_vlc, qtbot, monkeypatch):
        """If saved splitter sizes exist, they are restored on init."""
        from unittest.mock import MagicMock
        mock_settings = MagicMock()
        mock_settings.load_geometry.return_value = None
        mock_settings.load_splitter.return_value = [200, 500]
        mock_settings.load_last_playlist.return_value = None

        with patch("src.ui.main_window.AppSettings", return_value=mock_settings):
            from src.ui.main_window import MainWindow
            w = MainWindow()
            qtbot.addWidget(w)

        # splitter sizes should reflect the restored values
        mock_settings.load_splitter.assert_called_once()

    def test_open_playlist_saves_last_path(self, window, monkeypatch):
        """After successfully loading a file, the path is saved to settings."""
        from src.models.channel import Channel
        monkeypatch.setattr(
            "src.ui.main_window.QFileDialog.getOpenFileName",
            lambda *a, **kw: ("/home/user/playlist.m3u", ""),
        )
        monkeypatch.setattr(
            "src.ui.main_window.parse_m3u_file",
            lambda path: [Channel(url="http://a.com", name="Ch1", group="")],
        )
        mock_settings = MagicMock()
        window._settings = mock_settings

        window._open_playlist()

        mock_settings.save_last_playlist.assert_called_once_with("/home/user/playlist.m3u")


class TestOpenPlaylist:
    def test_open_playlist_dialog_uses_correct_filter(self, window, monkeypatch):
        """Dialog is opened with the M3U file filter."""
        mock_dialog = MagicMock(return_value=("", ""))
        monkeypatch.setattr(
            "src.ui.main_window.QFileDialog.getOpenFileName", mock_dialog
        )

        window._open_playlist()

        assert "M3U Playlists (*.m3u *.m3u8)" in str(mock_dialog.call_args)

    def test_open_playlist_loads_channels_and_updates_status(
        self, window, monkeypatch
    ):
        """Valid file path: channels are loaded and status bar updated."""
        monkeypatch.setattr(
            "src.ui.main_window.QFileDialog.getOpenFileName",
            MagicMock(return_value=("/path/test.m3u", "")),
        )
        monkeypatch.setattr(
            "src.ui.main_window.parse_m3u_file",
            MagicMock(
                return_value=[Channel(url="http://a.com", name="TestCh", group="")]
            ),
        )

        window._open_playlist()

        assert window._channel_list.count() > 0
        assert window.statusBar().currentMessage() == "1 channels loaded"

    def test_open_playlist_cancel_does_not_change_state(self, window, monkeypatch):
        """Cancelling the dialog leaves channel list and status bar unchanged."""
        monkeypatch.setattr(
            "src.ui.main_window.QFileDialog.getOpenFileName",
            MagicMock(return_value=("", "")),
        )
        load_channels_mock = MagicMock()
        monkeypatch.setattr(window._channel_list, "load_channels", load_channels_mock)

        window._open_playlist()

        assert load_channels_mock.call_count == 0
        assert window.statusBar().currentMessage() == "No playlist loaded"
