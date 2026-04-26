from __future__ import annotations

import pytest
from PyQt6.QtWidgets import QLabel

from src.v2.navigator import ScreenNavigator


class TestHistoryDepth:
    def test_history_capped_at_10(self, qtbot):
        nav = ScreenNavigator()
        qtbot.addWidget(nav)
        for i in range(12):
            nav.register(f"screen{i}", QLabel(f"screen{i}"))
        # navigate through all 12
        for i in range(12):
            nav.navigate(f"screen{i}")
        # go_back should only have 10 previous screens max
        for _ in range(10):
            nav.go_back()
        # after 10 go_backs, we should be at screen1 (screen0 was first, not in history)
        assert nav.current_screen() == "screen1"
        # one more go_back should do nothing (history empty)
        nav.go_back()
        assert nav.current_screen() == "screen1"
