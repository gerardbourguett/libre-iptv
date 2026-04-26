from __future__ import annotations

from src.v2.screens.settings_screen import SettingsScreen

_SECTIONS = ["general", "perfil", "playlist", "epg", "parental", "info"]


class TestSettingsScreenCreation:
    def test_creates_without_error(self, qtbot) -> None:
        screen = SettingsScreen()
        qtbot.addWidget(screen)
        assert screen is not None

    def test_default_section_is_general(self, qtbot) -> None:
        screen = SettingsScreen()
        qtbot.addWidget(screen)
        assert screen.selected_section() == "general"

    def test_section_count_is_six(self, qtbot) -> None:
        screen = SettingsScreen()
        qtbot.addWidget(screen)
        assert screen.section_count() == 6


class TestSettingsScreenNavigation:
    def test_select_epg_section(self, qtbot) -> None:
        screen = SettingsScreen()
        qtbot.addWidget(screen)
        screen.select_section("epg")
        assert screen.selected_section() == "epg"

    def test_select_parental_section(self, qtbot) -> None:
        screen = SettingsScreen()
        qtbot.addWidget(screen)
        screen.select_section("parental")
        assert screen.selected_section() == "parental"

    def test_select_info_section(self, qtbot) -> None:
        screen = SettingsScreen()
        qtbot.addWidget(screen)
        screen.select_section("info")
        assert screen.selected_section() == "info"

    def test_select_all_sections_valid(self, qtbot) -> None:
        screen = SettingsScreen()
        qtbot.addWidget(screen)
        for section in _SECTIONS:
            screen.select_section(section)
            assert screen.selected_section() == section

    def test_invalid_section_ignored(self, qtbot) -> None:
        screen = SettingsScreen()
        qtbot.addWidget(screen)
        screen.select_section("general")
        screen.select_section("nonexistent")
        assert screen.selected_section() == "general"

    def test_stack_index_changes_with_section(self, qtbot) -> None:
        screen = SettingsScreen()
        qtbot.addWidget(screen)
        for i, section in enumerate(_SECTIONS):
            screen.select_section(section)
            assert screen._section_stack.currentIndex() == i


class TestSettingsScreenSignals:
    def test_close_requested_signal(self, qtbot) -> None:
        screen = SettingsScreen()
        qtbot.addWidget(screen)
        fired: list[bool] = []
        screen.close_requested.connect(lambda: fired.append(True))
        screen._request_close()
        assert fired == [True]
