from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.models.programme import EpgChannel, Programme
from src.services.epg_service import EpgService


class TestEpgCache:
    def test_cache_miss_triggers_fetch(self, tmp_path: Path, qtbot: Any) -> None:
        service = EpgService(cache_dir=tmp_path, refresh_hours=24)
        with patch("src.services.epg_service.parse_xmltv_url") as mock_fetch:
            mock_fetch.return_value = (
                [EpgChannel(id="ch1", names=["Ch1"])],
                [Programme(channel="ch1", title="News", start="20260101000000 +0000", stop="20260101010000 +0000")],
            )
            with qtbot.waitSignal(service.epg_ready, timeout=2000):
                service.start("https://example.com/epg.xml")
            mock_fetch.assert_called_once_with("https://example.com/epg.xml")

    def test_cache_hit_loads_from_disk(self, tmp_path: Path, qtbot: Any) -> None:
        service = EpgService(cache_dir=tmp_path, refresh_hours=24)
        # Pre-populate cache
        cache_data = {
            "url": "https://example.com/epg.xml",
            "channels": [{"id": "ch1", "names": ["Ch1"], "icon": ""}],
            "programmes": [
                {"channel": "ch1", "title": "News", "start": "20260101000000 +0000", "stop": "20260101010000 +0000", "description": ""}
            ],
        }
        from hashlib import sha256
        key = sha256("https://example.com/epg.xml".encode()).hexdigest()
        cache_file = tmp_path / f"{key}.json"
        cache_file.write_text(json.dumps(cache_data), encoding="utf-8")

        with patch("src.services.epg_service.parse_xmltv_url") as mock_fetch:
            with qtbot.waitSignal(service.epg_ready, timeout=2000):
                service.start("https://example.com/epg.xml")
            mock_fetch.assert_not_called()

    def test_cache_expired_triggers_re_fetch(self, tmp_path: Path, qtbot: Any) -> None:
        service = EpgService(cache_dir=tmp_path, refresh_hours=24)
        cache_data = {
            "url": "https://example.com/epg.xml",
            "channels": [{"id": "ch1", "names": ["Ch1"], "icon": ""}],
            "programmes": [
                {"channel": "ch1", "title": "News", "start": "20260101000000 +0000", "stop": "20260101010000 +0000", "description": ""}
            ],
        }
        from hashlib import sha256
        key = sha256("https://example.com/epg.xml".encode()).hexdigest()
        cache_file = tmp_path / f"{key}.json"
        cache_file.write_text(json.dumps(cache_data), encoding="utf-8")
        # Set mtime to 48 hours ago
        old_mtime = time.time() - (48 * 3600)
        os.utime(cache_file, (old_mtime, old_mtime))

        with patch("src.services.epg_service.parse_xmltv_url") as mock_fetch:
            mock_fetch.return_value = (
                [EpgChannel(id="ch1", names=["Ch1"])],
                [Programme(channel="ch1", title="News", start="20260101000000 +0000", stop="20260101010000 +0000")],
            )
            with qtbot.waitSignal(service.epg_ready, timeout=2000):
                service.start("https://example.com/epg.xml")
            mock_fetch.assert_called_once_with("https://example.com/epg.xml")

    def test_cache_invalidated_on_url_change(self, tmp_path: Path, qtbot: Any) -> None:
        service = EpgService(cache_dir=tmp_path, refresh_hours=24)
        cache_data = {
            "url": "https://old.com/epg.xml",
            "channels": [{"id": "ch1", "names": ["Ch1"], "icon": ""}],
            "programmes": [
                {"channel": "ch1", "title": "News", "start": "20260101000000 +0000", "stop": "20260101010000 +0000", "description": ""}
            ],
        }
        from hashlib import sha256
        key = sha256("https://old.com/epg.xml".encode()).hexdigest()
        cache_file = tmp_path / f"{key}.json"
        cache_file.write_text(json.dumps(cache_data), encoding="utf-8")

        with patch("src.services.epg_service.parse_xmltv_url") as mock_fetch:
            mock_fetch.return_value = (
                [EpgChannel(id="ch2", names=["Ch2"])],
                [Programme(channel="ch2", title="Sports", start="20260101000000 +0000", stop="20260101010000 +0000")],
            )
            with qtbot.waitSignal(service.epg_ready, timeout=2000):
                service.start("https://new.com/epg.xml")
            mock_fetch.assert_called_once_with("https://new.com/epg.xml")
