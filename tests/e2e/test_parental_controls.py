from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PyQt6.QtCore import Qt

from src.i18n import init_translator
from src.models.channel import Channel
from src.profiles.manager import ProfileManager
from src.ui.channel_list import ChannelListWidget
from src.ui.main_window import MainWindow
from src.ui.pin_dialog import PinDialog


@pytest.fixture(autouse=True)
def translator(qapp):
    init_translator(locales_dir=None)


@pytest.fixture
def tmp_manager(tmp_path: Path) -> ProfileManager:
    return ProfileManager(base_dir=tmp_path)


@pytest.fixture
def channels() -> list[Channel]:
    return [
        Channel(url="http://cnn.com", name="CNN", group="News"),
        Channel(url="http://bbc.com", name="BBC", group="News"),
        Channel(url="http://espn.com", name="ESPN", group="Sports"),
    ]


@pytest.fixture
def main_window(qtbot, tmp_manager, channels):
    tmp_manager.create_profile("A", "#00bcd4")
    win = MainWindow(manager=tmp_manager)
    qtbot.addWidget(win)
    win._channels = channels
    win._reload_channel_list()
    return win


class TestBlockedChannelFlow:
    def test_blocked_channel_shows_lock(self, main_window):
        main_window._manager.block_channel("http://cnn.com")
        main_window._reload_channel_list()
        cnn_item = main_window._channel_list.item(1)
        assert "🔒" in cnn_item.text()

    def test_select_blocked_channel_shows_pin_dialog(self, main_window, qtbot, monkeypatch):
        main_window._manager.block_channel("http://cnn.com")
        main_window._reload_channel_list()

        dialog_shown = []
        original_exec = PinDialog.exec

        def mock_exec(self):
            dialog_shown.append(True)
            return 0  # rejected

        monkeypatch.setattr(PinDialog, "exec", mock_exec)
        cnn_item = main_window._channel_list.item(1)
        main_window._channel_list.itemClicked.emit(cnn_item)
        assert dialog_shown

    def test_wrong_pin_rejects_playback(self, main_window, qtbot, monkeypatch):
        main_window._manager.set_pin("1234")
        main_window._manager.block_channel("http://cnn.com")
        main_window._reload_channel_list()

        monkeypatch.setattr(
            PinDialog, "exec", lambda self: 1 if self._pin == "0000" else 0
        )
        monkeypatch.setattr(
            PinDialog, "pin_value", lambda self: "0000"
        )

        play_mock = MagicMock()
        monkeypatch.setattr(main_window._grid, "play_in_active", play_mock)

        cnn_item = main_window._channel_list.item(1)
        main_window._channel_list.itemClicked.emit(cnn_item)
        play_mock.assert_not_called()

    def test_correct_pin_allows_playback(self, main_window, qtbot, monkeypatch):
        main_window._manager.set_pin("1234")
        main_window._manager.block_channel("http://cnn.com")
        main_window._reload_channel_list()

        monkeypatch.setattr(
            PinDialog, "exec", lambda self: 1
        )
        monkeypatch.setattr(
            PinDialog, "pin_value", lambda self: "1234"
        )

        play_mock = MagicMock()
        monkeypatch.setattr(main_window._grid, "play_in_active", play_mock)

        cnn_item = main_window._channel_list.item(1)
        main_window._channel_list.itemClicked.emit(cnn_item)
        play_mock.assert_called_once()


class TestProfileIsolation:
    def test_switch_profile_swaps_blocklist(self, tmp_manager, channels, qtbot):
        tmp_manager.create_profile("A", "#00bcd4")
        tmp_manager.create_profile("B", "#4caf50")
        tmp_manager.block_channel("http://cnn.com")

        win = MainWindow(manager=tmp_manager)
        qtbot.addWidget(win)
        win._channels = channels
        win._reload_channel_list()

        # Profile A has CNN blocked
        assert "🔒" in win._channel_list.item(1).text()

        # Switch to Profile B
        profile_b = [p for p in tmp_manager.list_profiles() if p.name == "B"][0]
        tmp_manager.switch_profile(profile_b.id)
        win._on_profile_switched(profile_b)
        win._channels = channels
        win._reload_channel_list()

        # Profile B has no blocks
        assert "🔒" not in win._channel_list.item(1).text()


class TestPinManagementViaPanel:
    def test_set_pin_via_panel(self, main_window, qtbot):
        from src.ui.parental_panel import ParentalControlsPanel

        panel = ParentalControlsPanel(
            manager=main_window._manager, channels=main_window._channels
        )
        qtbot.addWidget(panel)

        panel._new_pin.setText("5678")
        panel._confirm_pin.setText("5678")
        panel._on_save_pin()

        assert main_window._manager.verify_pin("5678") is True

    def test_remove_pin_via_panel(self, main_window, qtbot):
        from src.ui.parental_panel import ParentalControlsPanel

        main_window._manager.set_pin("1234")
        panel = ParentalControlsPanel(
            manager=main_window._manager, channels=main_window._channels
        )
        qtbot.addWidget(panel)
        panel.refresh()

        panel._current_pin.setText("1234")
        panel._on_remove_pin()

        assert main_window._manager.active_profile().pin_hash == ""
