from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal

from src.models.profile import Profile
from src.profiles.manager import ProfileManager


class ProfileController(QObject):
    profile_changed = pyqtSignal(Profile)
    favorites_changed = pyqtSignal()

    def __init__(self, manager: ProfileManager, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._manager = manager

    def switch_profile(self, profile_id: str) -> None:
        """Delegates to manager, emits profile_changed."""
        self._manager.switch_profile(profile_id)
        self.profile_changed.emit(self._manager.active_profile())

    def toggle_favorite(self, channel_url: str) -> None:
        """Delegates to manager.save_active, emits favorites_changed."""
        self._manager.toggle_favorite(channel_url)
        self._manager.save_active()
        self.favorites_changed.emit()

    def add_to_recent(self, channel_url: str) -> None:
        """Delegates to manager.add_to_recent + save_active."""
        self._manager.add_to_recent(channel_url)
        self._manager.save_active()

    def active_profile(self) -> Profile:
        """Pass-through to manager.active_profile()."""
        return self._manager.active_profile()
