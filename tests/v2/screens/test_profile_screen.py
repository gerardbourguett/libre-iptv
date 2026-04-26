from __future__ import annotations

from src.models.profile import Profile
from src.v2.screens.profile_screen import ProfileScreen


def _profile(name: str, color: str = "#00bcd4", pid: str = "") -> Profile:
    return Profile(id=pid or name.lower(), name=name, color=color)


class TestProfileScreenCreation:
    def test_creates_without_profiles(self, qtbot) -> None:
        screen = ProfileScreen()
        qtbot.addWidget(screen)
        assert screen is not None

    def test_creates_with_profiles(self, qtbot) -> None:
        screen = ProfileScreen(profiles=[_profile("Alice"), _profile("Bob")])
        qtbot.addWidget(screen)
        assert screen is not None

    def test_profile_count_matches(self, qtbot) -> None:
        screen = ProfileScreen(profiles=[_profile("Alice"), _profile("Bob"), _profile("Carlos")])
        qtbot.addWidget(screen)
        assert screen.profile_count() == 3

    def test_empty_has_zero_profiles(self, qtbot) -> None:
        screen = ProfileScreen()
        qtbot.addWidget(screen)
        assert screen.profile_count() == 0


class TestProfileScreenCards:
    def test_card_names_match_profiles(self, qtbot) -> None:
        profiles = [_profile("Alice"), _profile("Bob")]
        screen = ProfileScreen(profiles=profiles)
        qtbot.addWidget(screen)
        names = screen.card_names()
        assert "Alice" in names
        assert "Bob" in names

    def test_add_card_always_present(self, qtbot) -> None:
        screen = ProfileScreen()
        qtbot.addWidget(screen)
        assert screen.has_add_card()

    def test_add_card_present_with_profiles(self, qtbot) -> None:
        screen = ProfileScreen(profiles=[_profile("Alice")])
        qtbot.addWidget(screen)
        assert screen.has_add_card()


class TestProfileScreenLoadProfiles:
    def test_load_profiles_updates_count(self, qtbot) -> None:
        screen = ProfileScreen()
        qtbot.addWidget(screen)
        screen.load_profiles([_profile("Alice"), _profile("Bob")])
        assert screen.profile_count() == 2

    def test_load_profiles_replaces_previous(self, qtbot) -> None:
        screen = ProfileScreen(profiles=[_profile("Old")])
        qtbot.addWidget(screen)
        screen.load_profiles([_profile("New1"), _profile("New2"), _profile("New3")])
        assert screen.profile_count() == 3
        assert "New1" in screen.card_names()
        assert "Old" not in screen.card_names()


class TestProfileScreenSignals:
    def test_profile_selected_signal_on_click(self, qtbot) -> None:
        alice = _profile("Alice", pid="alice-id")
        screen = ProfileScreen(profiles=[alice])
        qtbot.addWidget(screen)
        received: list[Profile] = []
        screen.profile_selected.connect(received.append)
        screen._cards[0].clicked.emit(alice)
        assert len(received) == 1
        assert received[0].name == "Alice"

    def test_add_profile_signal_on_click(self, qtbot) -> None:
        screen = ProfileScreen()
        qtbot.addWidget(screen)
        fired: list[bool] = []
        screen.add_profile_requested.connect(lambda: fired.append(True))
        screen._add_card.clicked.emit()
        assert fired == [True]
