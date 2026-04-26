from __future__ import annotations

import pytest
from PyQt6.QtWidgets import QLabel, QWidget

from src.v2.navigator import ScreenNavigator


class TestRegister:
    def test_register_adds_widget_to_stacked(self, qtbot):
        nav = ScreenNavigator()
        qtbot.addWidget(nav)
        widget = QLabel("home")
        nav.register("home", widget)
        assert nav.count() == 1
        assert nav.widget(0) is widget

    def test_register_multiple_widgets(self, qtbot):
        nav = ScreenNavigator()
        qtbot.addWidget(nav)
        nav.register("a", QLabel("a"))
        nav.register("b", QLabel("b"))
        assert nav.count() == 2
