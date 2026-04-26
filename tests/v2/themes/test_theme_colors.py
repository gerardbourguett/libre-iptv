from __future__ import annotations

import pytest


class TestThemeColors:
    def test_has_background_field(self):
        from src.v2.themes import ThemeColors
        tc = ThemeColors(background="#0d0d0d", surface="#1e1e1e", text="#e0e0e0", accent="#00bcd4")
        assert tc.background == "#0d0d0d"

    def test_has_surface_field(self):
        from src.v2.themes import ThemeColors
        tc = ThemeColors(background="#0d0d0d", surface="#1e1e1e", text="#e0e0e0", accent="#00bcd4")
        assert tc.surface == "#1e1e1e"

    def test_has_text_field(self):
        from src.v2.themes import ThemeColors
        tc = ThemeColors(background="#0d0d0d", surface="#1e1e1e", text="#e0e0e0", accent="#00bcd4")
        assert tc.text == "#e0e0e0"

    def test_has_accent_field(self):
        from src.v2.themes import ThemeColors
        tc = ThemeColors(background="#0d0d0d", surface="#1e1e1e", text="#e0e0e0", accent="#00bcd4")
        assert tc.accent == "#00bcd4"

    def test_is_frozen(self):
        from src.v2.themes import ThemeColors
        tc = ThemeColors(background="#0d0d0d", surface="#1e1e1e", text="#e0e0e0", accent="#00bcd4")
        with pytest.raises(AttributeError):
            tc.background = "#ffffff"
