from __future__ import annotations

from unittest.mock import Mock

import pytest
from PyQt6.QtWidgets import QMenuBar

from src.i18n import init_translator, t
from src.services.menu_builder import MenuBuilder


@pytest.fixture(autouse=True)
def translator(qapp):
    init_translator(locales_dir=None)


class TestMenuBuilderBuild:
    def test_build_returns_qmenubar(self, qtbot):
        """MenuBuilder.build returns a QMenuBar instance."""
        builder = MenuBuilder()
        callbacks = {k: Mock() for k in [
            "open_playlist", "open_url", "quit", "stop",
            "layout_single", "layout_dual", "layout_quad", "about",
        ]}
        bar = builder.build(callbacks)
        qtbot.addWidget(bar)
        assert isinstance(bar, QMenuBar)

    def test_menus_present(self, qtbot):
        """Bar contains File, Playback, View, and Help menus."""
        builder = MenuBuilder()
        callbacks = {k: Mock() for k in [
            "open_playlist", "open_url", "quit", "stop",
            "layout_single", "layout_dual", "layout_quad", "about",
        ]}
        bar = builder.build(callbacks)
        qtbot.addWidget(bar)
        titles = [a.text() for a in bar.actions()]
        assert t("menu.file") in titles
        assert t("menu.playback") in titles
        assert t("menu.view") in titles
        assert t("menu.help") in titles


class TestMenuBuilderActions:
    def _find_menu(self, bar, title: str):
        for action in bar.actions():
            if action.text() == title:
                return action.menu()
        return None

    def _find_action(self, menu, title: str):
        for action in menu.actions():
            if action.text() == title:
                return action
        return None

    def test_file_menu_has_open_playlist_and_quit(self, qtbot):
        builder = MenuBuilder()
        callbacks = {k: Mock() for k in [
            "open_playlist", "open_url", "quit", "stop",
            "layout_single", "layout_dual", "layout_quad", "about",
        ]}
        bar = builder.build(callbacks)
        qtbot.addWidget(bar)
        file_menu = self._find_menu(bar, t("menu.file"))
        assert file_menu is not None
        assert self._find_action(file_menu, t("menu.open_playlist")) is not None
        assert self._find_action(file_menu, t("menu.open_url")) is not None
        assert self._find_action(file_menu, t("menu.quit")) is not None

    def test_playback_menu_has_stop(self, qtbot):
        builder = MenuBuilder()
        callbacks = {k: Mock() for k in [
            "open_playlist", "open_url", "quit", "stop",
            "layout_single", "layout_dual", "layout_quad", "about",
        ]}
        bar = builder.build(callbacks)
        qtbot.addWidget(bar)
        pb_menu = self._find_menu(bar, t("menu.playback"))
        assert pb_menu is not None
        assert self._find_action(pb_menu, t("menu.stop")) is not None

    def test_view_menu_has_layout_submenu(self, qtbot):
        builder = MenuBuilder()
        callbacks = {k: Mock() for k in [
            "open_playlist", "open_url", "quit", "stop",
            "layout_single", "layout_dual", "layout_quad", "about",
        ]}
        bar = builder.build(callbacks)
        qtbot.addWidget(bar)
        view_menu = self._find_menu(bar, t("menu.view"))
        assert view_menu is not None
        layout_menu = None
        for action in view_menu.actions():
            if action.text() == t("layout.toolbar"):
                layout_menu = action.menu()
                break
        assert layout_menu is not None
        assert self._find_action(layout_menu, t("layout.single")) is not None
        assert self._find_action(layout_menu, t("layout.dual")) is not None
        assert self._find_action(layout_menu, t("layout.quad")) is not None

    def test_help_menu_has_about(self, qtbot):
        builder = MenuBuilder()
        callbacks = {k: Mock() for k in [
            "open_playlist", "open_url", "quit", "stop",
            "layout_single", "layout_dual", "layout_quad", "about",
        ]}
        bar = builder.build(callbacks)
        qtbot.addWidget(bar)
        help_menu = self._find_menu(bar, t("menu.help"))
        assert help_menu is not None
        assert self._find_action(help_menu, t("menu.about")) is not None


class TestMenuBuilderCallbacks:
    def _find_action(self, menu, title: str):
        for action in menu.actions():
            if action.text() == title:
                return action
        return None

    def _trigger_action(self, bar, menu_title: str, action_title: str):
        menu = None
        for action in bar.actions():
            if action.text() == menu_title:
                menu = action.menu()
                break
        assert menu is not None
        act = self._find_action(menu, action_title)
        assert act is not None
        act.trigger()
        return act

    def test_open_playlist_callback_triggered(self, qtbot):
        callbacks = {k: Mock() for k in [
            "open_playlist", "open_url", "quit", "stop",
            "layout_single", "layout_dual", "layout_quad", "about",
        ]}
        bar = MenuBuilder().build(callbacks)
        qtbot.addWidget(bar)
        self._trigger_action(bar, t("menu.file"), t("menu.open_playlist"))
        callbacks["open_playlist"].assert_called_once()

    def test_open_url_callback_triggered(self, qtbot):
        callbacks = {k: Mock() for k in [
            "open_playlist", "open_url", "quit", "stop",
            "layout_single", "layout_dual", "layout_quad", "about",
        ]}
        bar = MenuBuilder().build(callbacks)
        qtbot.addWidget(bar)
        self._trigger_action(bar, t("menu.file"), t("menu.open_url"))
        callbacks["open_url"].assert_called_once()

    def test_quit_callback_triggered(self, qtbot):
        callbacks = {k: Mock() for k in [
            "open_playlist", "open_url", "quit", "stop",
            "layout_single", "layout_dual", "layout_quad", "about",
        ]}
        bar = MenuBuilder().build(callbacks)
        qtbot.addWidget(bar)
        self._trigger_action(bar, t("menu.file"), t("menu.quit"))
        callbacks["quit"].assert_called_once()

    def test_stop_callback_triggered(self, qtbot):
        callbacks = {k: Mock() for k in [
            "open_playlist", "open_url", "quit", "stop",
            "layout_single", "layout_dual", "layout_quad", "about",
        ]}
        bar = MenuBuilder().build(callbacks)
        qtbot.addWidget(bar)
        self._trigger_action(bar, t("menu.playback"), t("menu.stop"))
        callbacks["stop"].assert_called_once()

    def test_layout_single_callback_triggered(self, qtbot):
        callbacks = {k: Mock() for k in [
            "open_playlist", "open_url", "quit", "stop",
            "layout_single", "layout_dual", "layout_quad", "about",
        ]}
        bar = MenuBuilder().build(callbacks)
        qtbot.addWidget(bar)
        view_menu = None
        for action in bar.actions():
            if action.text() == t("menu.view"):
                view_menu = action.menu()
                break
        assert view_menu is not None
        layout_menu = None
        for action in view_menu.actions():
            if action.text() == t("layout.toolbar"):
                layout_menu = action.menu()
                break
        assert layout_menu is not None
        act = self._find_action(layout_menu, t("layout.single"))
        assert act is not None
        act.trigger()
        callbacks["layout_single"].assert_called_once()

    def test_layout_dual_callback_triggered(self, qtbot):
        callbacks = {k: Mock() for k in [
            "open_playlist", "open_url", "quit", "stop",
            "layout_single", "layout_dual", "layout_quad", "about",
        ]}
        bar = MenuBuilder().build(callbacks)
        qtbot.addWidget(bar)
        view_menu = None
        for action in bar.actions():
            if action.text() == t("menu.view"):
                view_menu = action.menu()
                break
        assert view_menu is not None
        layout_menu = None
        for action in view_menu.actions():
            if action.text() == t("layout.toolbar"):
                layout_menu = action.menu()
                break
        assert layout_menu is not None
        act = self._find_action(layout_menu, t("layout.dual"))
        assert act is not None
        act.trigger()
        callbacks["layout_dual"].assert_called_once()

    def test_layout_quad_callback_triggered(self, qtbot):
        callbacks = {k: Mock() for k in [
            "open_playlist", "open_url", "quit", "stop",
            "layout_single", "layout_dual", "layout_quad", "about",
        ]}
        bar = MenuBuilder().build(callbacks)
        qtbot.addWidget(bar)
        view_menu = None
        for action in bar.actions():
            if action.text() == t("menu.view"):
                view_menu = action.menu()
                break
        assert view_menu is not None
        layout_menu = None
        for action in view_menu.actions():
            if action.text() == t("layout.toolbar"):
                layout_menu = action.menu()
                break
        assert layout_menu is not None
        act = self._find_action(layout_menu, t("layout.quad"))
        assert act is not None
        act.trigger()
        callbacks["layout_quad"].assert_called_once()

    def test_about_callback_triggered(self, qtbot):
        callbacks = {k: Mock() for k in [
            "open_playlist", "open_url", "quit", "stop",
            "layout_single", "layout_dual", "layout_quad", "about",
        ]}
        bar = MenuBuilder().build(callbacks)
        qtbot.addWidget(bar)
        self._trigger_action(bar, t("menu.help"), t("menu.about"))
        callbacks["about"].assert_called_once()


class TestMenuBuilderStateless:
    def test_multiple_builds_are_independent(self, qtbot):
        """MenuBuilder is stateless — each build produces independent bars."""
        builder = MenuBuilder()
        callbacks1 = {k: Mock() for k in [
            "open_playlist", "open_url", "quit", "stop",
            "layout_single", "layout_dual", "layout_quad", "about",
        ]}
        callbacks2 = {k: Mock() for k in [
            "open_playlist", "open_url", "quit", "stop",
            "layout_single", "layout_dual", "layout_quad", "about",
        ]}
        bar1 = builder.build(callbacks1)
        bar2 = builder.build(callbacks2)
        qtbot.addWidget(bar1)
        qtbot.addWidget(bar2)
        # Triggering an action on bar1 should not call bar2's callback
        file_menu = None
        for action in bar1.actions():
            if action.text() == t("menu.file"):
                file_menu = action.menu()
                break
        assert file_menu is not None
        for a in file_menu.actions():
            if a.text() == t("menu.open_playlist"):
                a.trigger()
                break
        callbacks1["open_playlist"].assert_called_once()
        callbacks2["open_playlist"].assert_not_called()
