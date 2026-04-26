from __future__ import annotations

from unittest.mock import Mock

import pytest

from src.services.profile_controller import ProfileController


@pytest.fixture
def mock_manager():
    from src.models.profile import Profile

    mgr = Mock()
    profile = Profile(id="pid-1", name="Test", color="#000")
    mgr.active_profile.return_value = profile
    mgr.switch_profile.return_value = profile
    return mgr


class TestProfileControllerSwitchProfile:
    def test_switch_profile_emits_profile_changed(self, qtbot, mock_manager):
        """switch_profile delegates to manager and emits profile_changed."""
        ctrl = ProfileController(mock_manager)
        with qtbot.waitSignal(ctrl.profile_changed, timeout=1000) as blocker:
            ctrl.switch_profile("pid-1")
        mock_manager.switch_profile.assert_called_once_with("pid-1")
        assert blocker.args[0] == mock_manager.active_profile.return_value


class TestProfileControllerToggleFavorite:
    def test_toggle_favorite_delegates_and_emits_favorites_changed(
        self, qtbot, mock_manager
    ):
        """toggle_favorite delegates to manager and emits favorites_changed."""
        ctrl = ProfileController(mock_manager)
        with qtbot.waitSignal(ctrl.favorites_changed, timeout=1000):
            ctrl.toggle_favorite("http://ch.com")
        mock_manager.toggle_favorite.assert_called_once_with("http://ch.com")
        mock_manager.save_active.assert_called_once()


class TestProfileControllerActiveProfile:
    def test_active_profile_returns_current_profile(self, mock_manager):
        """active_profile returns the manager's active profile."""
        ctrl = ProfileController(mock_manager)
        result = ctrl.active_profile()
        assert result == mock_manager.active_profile.return_value


class TestProfileControllerAddToRecent:
    def test_add_to_recent_delegates_and_saves(self, mock_manager):
        """add_to_recent delegates to manager and saves active profile."""
        ctrl = ProfileController(mock_manager)
        ctrl.add_to_recent("http://ch.com")
        mock_manager.add_to_recent.assert_called_once_with("http://ch.com")
        mock_manager.save_active.assert_called_once()
