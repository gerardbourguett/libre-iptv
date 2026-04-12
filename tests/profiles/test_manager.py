import json
from pathlib import Path

import pytest

from src.models.profile import AVATAR_COLORS
from src.profiles.manager import ProfileManager


@pytest.fixture
def tmp_manager(tmp_path: Path) -> ProfileManager:
    return ProfileManager(base_dir=tmp_path)


class TestNeedsWelcome:
    def test_true_when_no_index_file(self, tmp_path: Path):
        mgr = ProfileManager(base_dir=tmp_path)
        assert mgr.needs_welcome() is True

    def test_false_after_creating_a_profile(self, tmp_manager: ProfileManager):
        tmp_manager.create_profile("Test", AVATAR_COLORS[0])
        assert tmp_manager.needs_welcome() is False

    def test_true_when_index_exists_but_profiles_list_is_empty(self, tmp_path: Path):
        index = tmp_path / "index.json"
        index.write_text(json.dumps({"active": "", "profiles": []}))
        mgr = ProfileManager(base_dir=tmp_path)
        assert mgr.needs_welcome() is True


class TestCreateProfile:
    def test_returns_profile_with_given_name_and_color(
        self, tmp_manager: ProfileManager
    ):
        p = tmp_manager.create_profile("Mi Lista", "#00bcd4")
        assert p.name == "Mi Lista"
        assert p.color == "#00bcd4"

    def test_generates_unique_ids(self, tmp_manager: ProfileManager):
        p1 = tmp_manager.create_profile("A", "#00bcd4")
        p2 = tmp_manager.create_profile("B", "#4caf50")
        assert p1.id != p2.id

    def test_writes_json_to_disk(self, tmp_manager: ProfileManager, tmp_path: Path):
        p = tmp_manager.create_profile("Casa", "#00bcd4")
        profile_file = tmp_path / f"{p.id}.json"
        assert profile_file.exists()
        data = json.loads(profile_file.read_text())
        assert data["name"] == "Casa"

    def test_first_profile_becomes_active(self, tmp_manager: ProfileManager):
        p = tmp_manager.create_profile("First", "#00bcd4")
        assert tmp_manager.active_profile().id == p.id

    def test_second_profile_does_not_change_active(self, tmp_manager: ProfileManager):
        p1 = tmp_manager.create_profile("First", "#00bcd4")
        tmp_manager.create_profile("Second", "#4caf50")
        assert tmp_manager.active_profile().id == p1.id


class TestListProfiles:
    def test_empty_when_no_profiles(self, tmp_manager: ProfileManager):
        assert tmp_manager.list_profiles() == []

    def test_returns_all_created_profiles(self, tmp_manager: ProfileManager):
        tmp_manager.create_profile("B", "#00bcd4")
        tmp_manager.create_profile("A", "#4caf50")
        assert len(tmp_manager.list_profiles()) == 2

    def test_sorted_by_name(self, tmp_manager: ProfileManager):
        tmp_manager.create_profile("Zebra", "#00bcd4")
        tmp_manager.create_profile("Alpha", "#4caf50")
        names = [p.name for p in tmp_manager.list_profiles()]
        assert names == ["Alpha", "Zebra"]


class TestSwitchProfile:
    def test_switch_changes_active(self, tmp_manager: ProfileManager):
        tmp_manager.create_profile("A", "#00bcd4")
        p2 = tmp_manager.create_profile("B", "#4caf50")
        tmp_manager.switch_profile(p2.id)
        assert tmp_manager.active_profile().id == p2.id

    def test_switch_saves_previous_active_to_disk(
        self, tmp_manager: ProfileManager, tmp_path: Path
    ):
        p1 = tmp_manager.create_profile("A", "#00bcd4")
        p2 = tmp_manager.create_profile("B", "#4caf50")
        tmp_manager.add_to_recent("http://cnn.com")
        tmp_manager.switch_profile(p2.id)
        data = json.loads((tmp_path / f"{p1.id}.json").read_text())
        assert "http://cnn.com" in data["recent"]

    def test_switch_invalid_id_raises_key_error(self, tmp_manager: ProfileManager):
        tmp_manager.create_profile("A", "#00bcd4")
        with pytest.raises(KeyError):
            tmp_manager.switch_profile("nonexistent-id")

    def test_switch_persists_active_id_on_disk(
        self, tmp_manager: ProfileManager, tmp_path: Path
    ):
        tmp_manager.create_profile("A", "#00bcd4")
        p2 = tmp_manager.create_profile("B", "#4caf50")
        tmp_manager.switch_profile(p2.id)
        index = json.loads((tmp_path / "index.json").read_text())
        assert index["active"] == p2.id


class TestDeleteProfile:
    def test_delete_removes_from_list(self, tmp_manager: ProfileManager):
        p1 = tmp_manager.create_profile("A", "#00bcd4")
        p2 = tmp_manager.create_profile("B", "#4caf50")
        tmp_manager.delete_profile(p2.id)
        ids = [p.id for p in tmp_manager.list_profiles()]
        assert p2.id not in ids
        assert p1.id in ids

    def test_delete_removes_json_file(
        self, tmp_manager: ProfileManager, tmp_path: Path
    ):
        tmp_manager.create_profile("A", "#00bcd4")
        p2 = tmp_manager.create_profile("B", "#4caf50")
        tmp_manager.delete_profile(p2.id)
        assert not (tmp_path / f"{p2.id}.json").exists()

    def test_delete_only_profile_raises(self, tmp_manager: ProfileManager):
        p = tmp_manager.create_profile("Solo", "#00bcd4")
        with pytest.raises(ValueError):
            tmp_manager.delete_profile(p.id)

    def test_delete_active_switches_to_next(self, tmp_manager: ProfileManager):
        p1 = tmp_manager.create_profile("A", "#00bcd4")
        p2 = tmp_manager.create_profile("B", "#4caf50")
        tmp_manager.delete_profile(p1.id)
        assert tmp_manager.active_profile().id == p2.id


class TestRecentAndFavorites:
    def test_add_to_recent_inserts_at_front(self, tmp_manager: ProfileManager):
        tmp_manager.create_profile("A", "#00bcd4")
        tmp_manager.add_to_recent("http://bbc.com")
        tmp_manager.add_to_recent("http://cnn.com")
        assert tmp_manager.active_profile().recent[0] == "http://cnn.com"

    def test_add_to_recent_removes_duplicates(self, tmp_manager: ProfileManager):
        tmp_manager.create_profile("A", "#00bcd4")
        tmp_manager.add_to_recent("http://cnn.com")
        tmp_manager.add_to_recent("http://bbc.com")
        tmp_manager.add_to_recent("http://cnn.com")
        recent = tmp_manager.active_profile().recent
        assert recent.count("http://cnn.com") == 1
        assert recent[0] == "http://cnn.com"

    def test_add_to_recent_truncates_to_20(self, tmp_manager: ProfileManager):
        tmp_manager.create_profile("A", "#00bcd4")
        for i in range(25):
            tmp_manager.add_to_recent(f"http://channel{i}.com")
        assert len(tmp_manager.active_profile().recent) == 20

    def test_toggle_favorite_adds(self, tmp_manager: ProfileManager):
        tmp_manager.create_profile("A", "#00bcd4")
        result = tmp_manager.toggle_favorite("http://espn.com")
        assert result is True
        assert "http://espn.com" in tmp_manager.active_profile().favorites

    def test_toggle_favorite_removes(self, tmp_manager: ProfileManager):
        tmp_manager.create_profile("A", "#00bcd4")
        tmp_manager.toggle_favorite("http://espn.com")
        result = tmp_manager.toggle_favorite("http://espn.com")
        assert result is False
        assert "http://espn.com" not in tmp_manager.active_profile().favorites

    def test_toggle_favorite_no_duplicates(self, tmp_manager: ProfileManager):
        tmp_manager.create_profile("A", "#00bcd4")
        tmp_manager.toggle_favorite("http://espn.com")
        tmp_manager.toggle_favorite("http://espn.com")
        tmp_manager.toggle_favorite("http://espn.com")
        assert tmp_manager.active_profile().favorites.count("http://espn.com") == 1


class TestPersistenceAcrossInstances:
    def test_profiles_survive_manager_restart(self, tmp_path: Path):
        mgr1 = ProfileManager(base_dir=tmp_path)
        p = mgr1.create_profile("Persistido", "#00bcd4")

        mgr2 = ProfileManager(base_dir=tmp_path)
        assert len(mgr2.list_profiles()) == 1
        assert mgr2.active_profile().id == p.id
        assert mgr2.active_profile().name == "Persistido"
