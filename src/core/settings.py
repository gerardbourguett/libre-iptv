from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any


class SettingsManager:
    def __init__(self, config_dir: Path | None = None) -> None:
        if config_dir is None:
            from src.platform import get_config_dir
            config_dir = get_config_dir()
        self._config_dir = Path(config_dir)
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._data: dict[str, Any] = {}
        self._path = self._config_dir / "settings.json"
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            self._save()
            return
        try:
            text = self._path.read_text(encoding="utf-8")
            self._data = json.loads(text)
        except Exception:
            self._data = {}

    def _save(self) -> None:
        tmp = self._path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(self._data, indent=2), encoding="utf-8")
        tmp.replace(self._path)

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            parts = key.split(".")
            value: Any = self._data
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default
            return value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            parts = key.split(".")
            target = self._data
            for part in parts[:-1]:
                if part not in target or not isinstance(target[part], dict):
                    target[part] = {}
                target = target[part]
            target[parts[-1]] = value
            self._save()
