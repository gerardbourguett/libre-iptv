import pytest
from PyQt6.QtWidgets import QToolButton

from src.models.profile import AVATAR_COLORS
from src.profiles.manager import ProfileManager
from src.ui.profile_bar import ProfileSelectorBar


@pytest.fixture
def manager(tmp_path):
    mgr = ProfileManager(base_dir=tmp_path)
    mgr.create_profile("Casa", AVATAR_COLORS[0])
    return mgr


@pytest.fixture
def bar(manager, qtbot):
    w = ProfileSelectorBar(manager)
    qtbot.addWidget(w)
    return w


class TestProfileSelectorBarStructure:
    def test_shows_active_profile_name(self, bar, manager):
        assert manager.active_profile().name in bar.profile_name_text()

    def test_has_add_button(self, bar):
        buttons = bar.findChildren(QToolButton)
        assert any("+" in b.text() or "nuevo" in b.toolTip().lower() for b in buttons)

    def test_has_settings_button(self, bar):
        buttons = bar.findChildren(QToolButton)
        assert any("⚙" in b.text() or "config" in b.toolTip().lower() for b in buttons)


class TestProfileSelectorBarUpdate:
    def test_updates_when_profile_switches(self, manager, qtbot, tmp_path):
        p2 = manager.create_profile("Trabajo", AVATAR_COLORS[1])
        bar = ProfileSelectorBar(manager)
        qtbot.addWidget(bar)
        manager.switch_profile(p2.id)
        bar.refresh()
        assert "Trabajo" in bar.profile_name_text()

    def test_shows_initial_of_name_in_avatar(self, bar, manager):
        initial = manager.active_profile().name[0].upper()
        assert bar.avatar_initial() == initial
