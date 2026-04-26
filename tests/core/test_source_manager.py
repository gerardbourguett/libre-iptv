from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.core.source_manager import Source, SourceManager, SourceType


class TestSourceDataclass:
    def test_source_defaults(self) -> None:
        s = Source(id="abc", name="Test", type=SourceType.M3U_URL)
        assert s.enabled is True
        assert s.last_updated == ""
        assert s.auto_refresh is False
        assert s.refresh_interval == 60
        assert s.url == ""
        assert s.path == ""

    def test_source_custom_values(self) -> None:
        s = Source(
            id="abc",
            name="Test",
            type=SourceType.XTREAM,
            enabled=False,
            last_updated="2026-04-26T12:00:00Z",
            auto_refresh=True,
            refresh_interval=30,
            url="http://x.com",
            path="/tmp/x.m3u",
        )
        assert s.type == SourceType.XTREAM
        assert s.enabled is False
        assert s.last_updated == "2026-04-26T12:00:00Z"
        assert s.auto_refresh is True
        assert s.refresh_interval == 30
        assert s.url == "http://x.com"
        assert s.path == "/tmp/x.m3u"


class TestSourceManagerAdd:
    def test_add_source_assigns_uuid(self, tmp_path: Path) -> None:
        sm = SourceManager(config_dir=tmp_path)
        source = sm.add_source(name="Mi Lista", type_=SourceType.M3U_URL, url="http://x.com/pl.m3u")
        assert len(source.id) == 36  # uuid4
        assert source.name == "Mi Lista"
        assert source.type == SourceType.M3U_URL
        assert source.url == "http://x.com/pl.m3u"
        assert source.enabled is True

    def test_add_source_persists(self, tmp_path: Path) -> None:
        sm = SourceManager(config_dir=tmp_path)
        sm.add_source(name="Mi Lista", type_=SourceType.M3U_URL, url="http://x.com/pl.m3u")
        sources_file = tmp_path / "sources.json"
        assert sources_file.exists()
        data = json.loads(sources_file.read_text(encoding="utf-8"))
        assert len(data) == 1
        assert data[0]["name"] == "Mi Lista"


class TestSourceManagerList:
    def test_list_empty(self, tmp_path: Path) -> None:
        sm = SourceManager(config_dir=tmp_path)
        assert sm.list_sources() == []

    def test_list_returns_sources(self, tmp_path: Path) -> None:
        sm = SourceManager(config_dir=tmp_path)
        sm.add_source(name="A", type_=SourceType.M3U_URL, url="http://a.com")
        sm.add_source(name="B", type_=SourceType.M3U_FILE, path="/tmp/b.m3u")
        sources = sm.list_sources()
        assert len(sources) == 2
        assert {s.name for s in sources} == {"A", "B"}


class TestSourceManagerEnableDisable:
    def test_disable_source(self, tmp_path: Path) -> None:
        sm = SourceManager(config_dir=tmp_path)
        source = sm.add_source(name="A", type_=SourceType.M3U_URL, url="http://a.com")
        sm.disable(source.id)
        s = sm.get_source(source.id)
        assert s is not None
        assert s.enabled is False

    def test_enable_source(self, tmp_path: Path) -> None:
        sm = SourceManager(config_dir=tmp_path)
        source = sm.add_source(name="A", type_=SourceType.M3U_URL, url="http://a.com")
        sm.disable(source.id)
        sm.enable(source.id)
        s = sm.get_source(source.id)
        assert s is not None
        assert s.enabled is True

    def test_disable_persists(self, tmp_path: Path) -> None:
        sm = SourceManager(config_dir=tmp_path)
        source = sm.add_source(name="A", type_=SourceType.M3U_URL, url="http://a.com")
        sm.disable(source.id)
        sm2 = SourceManager(config_dir=tmp_path)
        s = sm2.get_source(source.id)
        assert s is not None
        assert s.enabled is False


class TestSourceManagerDelete:
    def test_delete_source(self, tmp_path: Path) -> None:
        sm = SourceManager(config_dir=tmp_path)
        source = sm.add_source(name="A", type_=SourceType.M3U_URL, url="http://a.com")
        sm.delete(source.id)
        assert sm.get_source(source.id) is None
        assert sm.list_sources() == []

    def test_delete_persists(self, tmp_path: Path) -> None:
        sm = SourceManager(config_dir=tmp_path)
        source = sm.add_source(name="A", type_=SourceType.M3U_URL, url="http://a.com")
        sm.delete(source.id)
        sm2 = SourceManager(config_dir=tmp_path)
        assert sm2.get_source(source.id) is None


class TestSourceManagerLoad:
    def test_load_from_existing_file(self, tmp_path: Path) -> None:
        data = [
            {
                "id": "src-1",
                "name": "Legacy",
                "type": "m3u_url",
                "enabled": True,
                "last_updated": "",
                "auto_refresh": False,
                "refresh_interval": 60,
                "url": "http://legacy.com",
                "path": "",
            }
        ]
        (tmp_path / "sources.json").write_text(json.dumps(data), encoding="utf-8")
        sm = SourceManager(config_dir=tmp_path)
        sources = sm.list_sources()
        assert len(sources) == 1
        assert sources[0].id == "src-1"
        assert sources[0].name == "Legacy"
        assert sources[0].type == SourceType.M3U_URL
