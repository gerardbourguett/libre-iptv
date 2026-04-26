from __future__ import annotations

import pytest
from PyQt6.QtGui import QPixmap

from src.ui.logo_loader import LogoCache


class TestLogoCache:
    @pytest.fixture
    def cache(self):
        from src.ui.logo_loader import LogoCache

        return LogoCache(maxsize=200)

    def test_get_miss_returns_none(self, cache):
        """S1: get() on unknown URL returns None."""
        assert cache.get("http://example.com/logo.png") is None

    def test_put_and_get_hit_returns_pixmap(self, cache, qtbot):
        """S2: put() then get() returns the stored pixmap."""
        url = "http://example.com/logo.png"
        pixmap = QPixmap(32, 32)
        cache.put(url, pixmap)
        result = cache.get(url)
        assert result is pixmap

    def test_contains_checks_key_existence(self, cache, qtbot):
        """S3: __contains__ reflects whether a URL was cached."""
        url = "http://example.com/logo.png"
        assert url not in cache
        cache.put(url, QPixmap(32, 32))
        assert url in cache

    def test_eviction_at_capacity_removes_lru(self, cache, qtbot):
        """S4: when maxsize reached, least recently used entry is evicted."""
        # Fill cache to capacity with 3 items (small for test)
        small = LogoCache(maxsize=3)
        small.put("a", QPixmap(1, 1))
        small.put("b", QPixmap(1, 1))
        small.put("c", QPixmap(1, 1))
        assert "a" in small
        assert "b" in small
        assert "c" in small

        # Access 'a' to make 'b' the LRU
        small.get("a")
        # Add new entry — should evict 'b'
        small.put("d", QPixmap(1, 1))
        assert "a" in small
        assert "b" not in small
        assert "c" in small
        assert "d" in small

    def test_get_updates_recency(self, cache, qtbot):
        """S5: get() moves entry to most-recently-used side."""
        small = LogoCache(maxsize=2)
        small.put("a", QPixmap(1, 1))
        small.put("b", QPixmap(1, 1))

        # Access 'a' so 'b' becomes LRU
        small.get("a")
        small.put("c", QPixmap(1, 1))

        assert "a" in small
        assert "b" not in small
        assert "c" in small

    def test_put_updates_recency_for_existing_key(self, cache, qtbot):
        """S6: put() on existing key updates value and recency."""
        small = LogoCache(maxsize=2)
        small.put("a", QPixmap(1, 1))
        small.put("b", QPixmap(1, 1))

        # Re-put 'a' so 'b' becomes LRU
        small.put("a", QPixmap(2, 2))
        small.put("c", QPixmap(1, 1))

        assert "a" in small
        assert "b" not in small
        assert "c" in small

    def test_default_maxsize_is_200(self, qtbot):
        """S7: default maxsize is 200."""
        from src.ui.logo_loader import LogoCache

        c = LogoCache()
        # Fill to 200 and verify 201st evicts first
        for i in range(200):
            c.put(str(i), QPixmap(1, 1))
        assert "0" in c
        c.put("200", QPixmap(1, 1))
        assert "0" not in c
        assert "200" in c
