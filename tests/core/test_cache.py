from __future__ import annotations

import gzip
import time
from pathlib import Path

import pytest

from src.models.channel import Channel
from src.models.programme import EpgChannel, Programme
from src.core.cache import ChannelCache, EpgCache, LogoCache


class TestChannelCache:
    def test_put_and_get(self, tmp_path: Path) -> None:
        cache = ChannelCache(cache_dir=tmp_path)
        channels = [Channel(url="http://x.com", name="X")]
        cache.put("src1", channels)
        result = cache.get("src1")
        assert result is not None
        assert len(result) == 1
        assert result[0].name == "X"

    def test_get_returns_none_when_expired(self, tmp_path: Path) -> None:
        cache = ChannelCache(cache_dir=tmp_path)
        channels = [Channel(url="http://x.com", name="X")]
        cache.put("src1", channels)
        # Manually set timestamp to 25 hours ago
        cache_file = tmp_path / "channels" / "src1.json"
        data = {
            "timestamp": time.time() - 25 * 3600,
            "channels": [ch.to_dict() for ch in channels],
        }
        cache_file.write_text(__import__("json").dumps(data), encoding="utf-8")
        assert cache.get("src1") is None

    def test_get_returns_none_when_missing(self, tmp_path: Path) -> None:
        cache = ChannelCache(cache_dir=tmp_path)
        assert cache.get("missing") is None

    def test_invalidate_removes_cache(self, tmp_path: Path) -> None:
        cache = ChannelCache(cache_dir=tmp_path)
        channels = [Channel(url="http://x.com", name="X")]
        cache.put("src1", channels)
        cache.invalidate("src1")
        assert cache.get("src1") is None


class TestEpgCache:
    def test_put_and_get(self, tmp_path: Path) -> None:
        cache = EpgCache(cache_dir=tmp_path)
        channels = [EpgChannel(id="bbc1", names=["BBC One"])]
        programmes = [Programme(channel="bbc1", title="News", start="20260101000000 +0000", stop="20260101010000 +0000")]
        cache.put("src1", channels, programmes)
        result = cache.get("src1")
        assert result is not None
        assert len(result[0]) == 1
        assert len(result[1]) == 1
        assert result[1][0].title == "News"

    def test_get_returns_none_when_expired(self, tmp_path: Path) -> None:
        cache = EpgCache(cache_dir=tmp_path)
        channels = [EpgChannel(id="bbc1", names=["BBC One"])]
        programmes = [Programme(channel="bbc1", title="News", start="20260101000000 +0000", stop="20260101010000 +0000")]
        cache.put("src1", channels, programmes)
        # Manually set timestamp to 13 hours ago
        cache_file = tmp_path / "epg" / "src1.json"
        data = {
            "timestamp": time.time() - 13 * 3600,
            "channels": [ch.to_dict() for ch in channels],
            "programmes": [p.to_dict() for p in programmes],
        }
        cache_file.write_text(__import__("json").dumps(data), encoding="utf-8")
        assert cache.get("src1") is None

    def test_get_returns_none_when_missing(self, tmp_path: Path) -> None:
        cache = EpgCache(cache_dir=tmp_path)
        assert cache.get("missing") is None

    def test_invalidate_removes_cache(self, tmp_path: Path) -> None:
        cache = EpgCache(cache_dir=tmp_path)
        channels = [EpgChannel(id="bbc1", names=["BBC One"])]
        programmes = [Programme(channel="bbc1", title="News", start="20260101000000 +0000", stop="20260101010000 +0000")]
        cache.put("src1", channels, programmes)
        cache.invalidate("src1")
        assert cache.get("src1") is None


class TestLogoCache:
    def test_save_and_load(self, tmp_path: Path) -> None:
        cache = LogoCache(cache_dir=tmp_path)
        logo_data = b"\x89PNG\r\n\x1a\nfakepng"
        cache.put("http://logo.png", logo_data)
        result = cache.get("http://logo.png")
        assert result == logo_data

    def test_get_returns_none_when_missing(self, tmp_path: Path) -> None:
        cache = LogoCache(cache_dir=tmp_path)
        assert cache.get("http://missing.png") is None

    def test_invalidate_removes_cache(self, tmp_path: Path) -> None:
        cache = LogoCache(cache_dir=tmp_path)
        logo_data = b"\x89PNG\r\n\x1a\nfakepng"
        cache.put("http://logo.png", logo_data)
        cache.invalidate("http://logo.png")
        assert cache.get("http://logo.png") is None

    def test_disk_file_exists(self, tmp_path: Path) -> None:
        cache = LogoCache(cache_dir=tmp_path)
        logo_data = b"\x89PNG\r\n\x1a\nfakepng"
        cache.put("http://logo.png", logo_data)
        import hashlib
        expected_hash = hashlib.sha256("http://logo.png".encode()).hexdigest()[:16]
        assert (tmp_path / "logos" / f"{expected_hash}.png").exists()
