from __future__ import annotations

from src.v2.themes import Theme


class TestThemeEnum:
    def test_midnight_colors(self):
        assert Theme.MIDNIGHT.value.background == "#0d0d0d"
        assert Theme.MIDNIGHT.value.surface == "#1e1e1e"
        assert Theme.MIDNIGHT.value.text == "#e0e0e0"
        assert Theme.MIDNIGHT.value.accent == "#00bcd4"

    def test_ocean_colors(self):
        assert Theme.OCEAN.value.background == "#0a192f"
        assert Theme.OCEAN.value.surface == "#112240"
        assert Theme.OCEAN.value.text == "#ccd6f6"
        assert Theme.OCEAN.value.accent == "#64ffda"

    def test_ember_colors(self):
        assert Theme.EMBER.value.background == "#1a0a0a"
        assert Theme.EMBER.value.surface == "#2d1111"
        assert Theme.EMBER.value.text == "#e0d0c0"
        assert Theme.EMBER.value.accent == "#ff6b35"

    def test_abyss_colors(self):
        assert Theme.ABYSS.value.background == "#0a0a1a"
        assert Theme.ABYSS.value.surface == "#141428"
        assert Theme.ABYSS.value.text == "#b8c0cc"
        assert Theme.ABYSS.value.accent == "#7b68ee"
