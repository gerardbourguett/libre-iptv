from __future__ import annotations

import pytest
from PyQt6.QtWidgets import QLabel

from src.v2.navigator import ScreenNavigator


class TestGoBack:
    def test_go_back_pops_history(self, qtbot):
        nav = ScreenNavigator()
        qtbot.addWidget(nav)
        nav.register("home", QLabel("home"))
        nav.register("live", QLabel("live"))
        nav.register("vod", QLabel("vod"))
        nav.navigate("home")
        nav.navigate("live")
        nav.navigate("vod")
        nav.go_back()
        assert nav.current_screen() == "live"
        nav.go_back()
        assert nav.current_screen() == "home"

    def test_go_back_on_empty_stack_does_nothing(self, qtbot):
        nav = ScreenNavigator()
        qtbot.addWidget(nav)
        nav.register("home", QLabel("home"))
        nav.navigate("home")
        # history is empty because this is the first navigation
        assert nav.current_screen() == "home"
        nav.go_back()
        assert nav.current_screen() == "home"

    def test_go_back_emits_screen_changed(self, qtbot):
        nav = ScreenNavigator()
        qtbot.addWidget(nav)
        nav.register("home", QLabel("home"))
        nav.register("live", QLabel("live"))
        nav.navigate("home")
        nav.navigate("live")
        with qtbot.waitSignal(nav.screen_changed, timeout=1000) as blocker:
            nav.go_back()
        assert blocker.args[0] == "home"
