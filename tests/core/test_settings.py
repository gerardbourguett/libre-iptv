from __future__ import annotations

import json
import threading
from pathlib import Path

import pytest

from src.core.settings import SettingsManager


class TestSettingsManagerGetSet:
    def test_get_existing_key(self, tmp_path: Path) -> None:
        settings = SettingsManager(config_dir=tmp_path)
        settings.set("volume", 80)
        assert settings.get("volume") == 80

    def test_get_missing_key_returns_none(self, tmp_path: Path) -> None:
        settings = SettingsManager(config_dir=tmp_path)
        assert settings.get("missing") is None

    def test_get_missing_key_with_default(self, tmp_path: Path) -> None:
        settings = SettingsManager(config_dir=tmp_path)
        assert settings.get("missing", "default") == "default"


class TestSettingsManagerDotPath:
    def test_set_nested_dot_path(self, tmp_path: Path) -> None:
        settings = SettingsManager(config_dir=tmp_path)
        settings.set("player.volume", 80)
        assert settings.get("player.volume") == 80

    def test_set_multiple_nested_keys(self, tmp_path: Path) -> None:
        settings = SettingsManager(config_dir=tmp_path)
        settings.set("player.volume", 80)
        settings.set("player.muted", True)
        settings.set("ui.theme", "dark")
        assert settings.get("player.volume") == 80
        assert settings.get("player.muted") is True
        assert settings.get("ui.theme") == "dark"

    def test_get_nested_section_as_dict(self, tmp_path: Path) -> None:
        settings = SettingsManager(config_dir=tmp_path)
        settings.set("player.volume", 80)
        settings.set("player.muted", True)
        assert settings.get("player") == {"volume": 80, "muted": True}

    def test_get_missing_nested_key(self, tmp_path: Path) -> None:
        settings = SettingsManager(config_dir=tmp_path)
        assert settings.get("player.bass") is None

    def test_overwrite_nested_value(self, tmp_path: Path) -> None:
        settings = SettingsManager(config_dir=tmp_path)
        settings.set("player.volume", 80)
        settings.set("player.volume", 90)
        assert settings.get("player.volume") == 90


class TestSettingsManagerPersistence:
    def test_creates_file_on_first_set(self, tmp_path: Path) -> None:
        settings = SettingsManager(config_dir=tmp_path)
        settings.set("key", "value")
        assert (tmp_path / "settings.json").exists()

    def test_persists_to_json(self, tmp_path: Path) -> None:
        settings = SettingsManager(config_dir=tmp_path)
        settings.set("player.volume", 80)
        settings.set("ui.theme", "dark")
        raw = json.loads((tmp_path / "settings.json").read_text(encoding="utf-8"))
        assert raw == {"player": {"volume": 80}, "ui": {"theme": "dark"}}

    def test_loads_existing_file(self, tmp_path: Path) -> None:
        data = {"general": {"lang": "es"}, "player": {"volume": 50}}
        (tmp_path / "settings.json").write_text(json.dumps(data), encoding="utf-8")
        settings = SettingsManager(config_dir=tmp_path)
        assert settings.get("general.lang") == "es"
        assert settings.get("player.volume") == 50

    def test_creates_file_on_init_if_missing(self, tmp_path: Path) -> None:
        settings = SettingsManager(config_dir=tmp_path)
        assert (tmp_path / "settings.json").exists()
        raw = json.loads((tmp_path / "settings.json").read_text(encoding="utf-8"))
        assert raw == {}


class TestSettingsManagerThreadSafety:
    def test_concurrent_writes(self, tmp_path: Path) -> None:
        settings = SettingsManager(config_dir=tmp_path)
        errors: list[Exception] = []

        def writer(key: str, value: int) -> None:
            try:
                for i in range(50):
                    settings.set(key, value + i)
            except Exception as exc:
                errors.append(exc)

        t1 = threading.Thread(target=writer, args=("a", 0))
        t2 = threading.Thread(target=writer, args=("b", 100))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert not errors
        # File must be valid JSON
        raw = json.loads((tmp_path / "settings.json").read_text(encoding="utf-8"))
        assert "a" in raw
        assert "b" in raw
