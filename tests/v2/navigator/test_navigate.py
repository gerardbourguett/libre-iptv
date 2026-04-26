from __future__ import annotations

import pytest
from PyQt6.QtWidgets import QLabel

from src.v2.navigator import ScreenNavigator


class TestNavigate:
    def test_navigate_switches_screen(self, qtbot):
        nav = ScreenNavigator()
        qtbot.addWidget(nav)
        nav.register("home", QLabel("home"))
        nav.register("live", QLabel("live"))
        nav.navigate("live")
        assert nav.currentIndex() == 1

    def test_navigate_emits_screen_changed(self, qtbot):
        nav = ScreenNavigator()
        qtbot.addWidget(nav)
        nav.register("home", QLabel("home"))
        nav.register("live", QLabel("live"))
        with qtbot.waitSignal(nav.screen_changed, timeout=1000) as blocker:
            nav.navigate("live")
        assert blocker.args[0] == "live"

    def test_navigate_pushes_previous_to_history(self, qtbot):
        nav = ScreenNavigator()
        qtbot.addWidget(nav)
        nav.register("home", QLabel("home"))
        nav.register("live", QLabel("live"))
        nav.navigate("home")
        nav.navigate("live")
        assert nav.current_screen() == "live"
        # go_back should return to home
        nav.go_back()
        assert nav.current_screen() == "home"
