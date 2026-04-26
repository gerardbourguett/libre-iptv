from __future__ import annotations

from typing import Any

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QStackedWidget, QWidget


class ScreenNavigator(QStackedWidget):
    screen_changed = pyqtSignal(str)
    play_requested = pyqtSignal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._screens: dict[str, QWidget] = {}
        self._history: list[str] = []
        self._current: str = ""
        self._play_on_navigate: Any = None

    def register(self, name: str, widget: QWidget) -> None:
        self._screens[name] = widget
        self.addWidget(widget)

    def navigate(self, name: str) -> None:
        if name not in self._screens:
            return
        if self._current and self._current != name:
            self._history.append(self._current)
            if len(self._history) > 10:
                self._history.pop(0)
        self._current = name
        widget = self._screens[name]
        self.setCurrentWidget(widget)
        self.screen_changed.emit(name)
        if self._play_on_navigate is not None:
            self.play_requested.emit(self._play_on_navigate)
            self._play_on_navigate = None
        self._save_last_screen(name)

    def go_back(self) -> None:
        if not self._history:
            return
        previous = self._history.pop()
        self._current = previous
        widget = self._screens[previous]
        self.setCurrentWidget(widget)
        self.screen_changed.emit(previous)

    def current_screen(self) -> str:
        return self._current

    def set_play_on_navigate(self, channel: Any | None) -> None:
        self._play_on_navigate = channel

    def _save_last_screen(self, name: str) -> None:
        # Hook for persistence; overridden in tests or wired by caller
        pass

    def _load_last_screen(self) -> str:
        return ""

    def restore_last_screen(self) -> None:
        last = self._load_last_screen()
        if last and last in self._screens:
            self.navigate(last)
        elif self._screens:
            first = next(iter(self._screens))
            self.navigate(first)
