from __future__ import annotations

import pytest

from src.models.channel import Channel
from src.models.profile import Profile
from src.v2.screens.home_screen import HomeScreen


def _profile() -> Profile:
    return Profile(id="p1", name="Test", color="#e50914")


def _channel(name: str = "Canal 1", url: str = "http://a.com/stream") -> Channel:
    return Channel(url=url, name=name)


class TestHomeScreenEmptyState:
    """HomeScreen shows empty state when no channels are loaded.

    NOTE: Uses isHidden() instead of isVisible() because Qt requires all
    ancestors to be shown for isVisible() to return True. isHidden() correctly
    reflects whether setVisible(False) was called, regardless of parent state.
    """

    def test_empty_state_not_hidden_on_init(self, qtbot):
        home = HomeScreen()
        qtbot.addWidget(home)
        assert not home._empty.isHidden()

    def test_scroll_hidden_on_init(self, qtbot):
        home = HomeScreen()
        qtbot.addWidget(home)
        assert home._scroll.isHidden()

    def test_loading_hidden_on_init(self, qtbot):
        home = HomeScreen()
        qtbot.addWidget(home)
        assert home._loading.isHidden()

    def test_empty_state_shown_after_populate_with_no_channels(self, qtbot):
        home = HomeScreen()
        qtbot.addWidget(home)
        home.populate([], _profile())
        assert not home._empty.isHidden()
        assert home._scroll.isHidden()

    def test_channels_state_after_populate_with_channels(self, qtbot):
        home = HomeScreen()
        qtbot.addWidget(home)
        ch = _channel()
        home.populate([ch], _profile())
        assert home._empty.isHidden()
        assert not home._scroll.isHidden()

    def test_loading_hidden_when_channels_present(self, qtbot):
        home = HomeScreen()
        qtbot.addWidget(home)
        home.populate([_channel()], _profile())
        assert home._loading.isHidden()

    def test_set_loading_true_shows_loading_widget(self, qtbot):
        home = HomeScreen()
        qtbot.addWidget(home)
        home.set_loading(True)
        assert not home._loading.isHidden()
        assert home._empty.isHidden()
        assert home._scroll.isHidden()

    def test_set_loading_false_returns_to_empty_state(self, qtbot):
        home = HomeScreen()
        qtbot.addWidget(home)
        home.set_loading(True)
        home.set_loading(False)
        assert not home._empty.isHidden()
        assert home._loading.isHidden()

    def test_load_playlist_requested_signal_emitted_on_button_click(self, qtbot):
        from PyQt6.QtWidgets import QPushButton

        home = HomeScreen()
        qtbot.addWidget(home)
        btn = home._empty.findChild(QPushButton, "btn_load_playlist")
        assert btn is not None, "button 'btn_load_playlist' not found in empty state"
        with qtbot.waitSignal(home.load_playlist_requested, timeout=1000):
            btn.click()

    def test_repopulate_with_no_channels_returns_to_empty_state(self, qtbot):
        """After showing channels, re-populating with [] goes back to empty state."""
        home = HomeScreen()
        qtbot.addWidget(home)
        home.populate([_channel()], _profile())
        assert not home._scroll.isHidden()
        home.populate([], _profile())
        assert not home._empty.isHidden()
        assert home._scroll.isHidden()
