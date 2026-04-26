from __future__ import annotations

import pytest
from PyQt6.QtWidgets import QLabel

from src.v2.navigator import ScreenNavigator


class TestLastScreen:
    def test_last_screen_persisted_to_profile_prefs(self, qtbot, monkeypatch):
        nav = ScreenNavigator()
        qtbot.addWidget(nav)
        nav.register("home", QLabel("home"))
        nav.register("live", QLabel("live"))

        saved = {}

        def mock_save_last(screen: str) -> None:
            saved["last_screen"] = screen

        monkeypatch.setattr(nav, "_save_last_screen", mock_save_last)
        nav.navigate("live")
        assert saved.get("last_screen") == "live"

    def test_restore_last_screen_on_startup(self, qtbot, monkeypatch):
        nav = ScreenNavigator()
        qtbot.addWidget(nav)
        nav.register("home", QLabel("home"))
        nav.register("live", QLabel("live"))

        monkeypatch.setattr(nav, "_load_last_screen", lambda: "live")
        nav.restore_last_screen()
        assert nav.current_screen() == "live"
