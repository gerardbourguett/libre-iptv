from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtWidgets import QMenuBar

from src.i18n import t


class MenuBuilder:
    """Builds the application menu bar from a callback dict."""

    def build(self, actions: dict[str, Callable[..., object]]) -> QMenuBar:
        """
        actions keys: open_playlist, open_url, quit, stop,
                      layout_single, layout_dual, layout_quad, about
        Returns: fully-constructed QMenuBar with all menus wired.
        """
        bar = QMenuBar()

        file_menu = bar.addMenu(t("menu.file"))
        assert file_menu is not None
        file_menu.addAction(t("menu.open_playlist"), actions["open_playlist"])
        file_menu.addAction(t("menu.open_url"), actions["open_url"])
        file_menu.addSeparator()
        file_menu.addAction(t("menu.quit"), actions["quit"])

        playback_menu = bar.addMenu(t("menu.playback"))
        assert playback_menu is not None
        playback_menu.addAction(t("menu.stop"), actions["stop"])

        view_menu = bar.addMenu(t("menu.view"))
        assert view_menu is not None
        layout_menu = view_menu.addMenu(t("layout.toolbar"))
        assert layout_menu is not None
        layout_menu.addAction(t("layout.single"), actions["layout_single"])
        layout_menu.addAction(t("layout.dual"), actions["layout_dual"])
        layout_menu.addAction(t("layout.quad"), actions["layout_quad"])

        help_menu = bar.addMenu(t("menu.help"))
        assert help_menu is not None
        help_menu.addAction(t("menu.about"), actions["about"])

        return bar
