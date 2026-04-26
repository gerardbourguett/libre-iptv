from __future__ import annotations

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

from src.v2.themes import Theme, apply_theme


class TestApplyTheme:
    def test_sets_window_background(self, qapp):
        apply_theme(Theme.MIDNIGHT, qapp)
        palette = qapp.palette()
        bg = palette.color(QPalette.ColorRole.Window)
        assert bg.name() == "#0d0d0d"

    def test_sets_window_text(self, qapp):
        apply_theme(Theme.OCEAN, qapp)
        palette = qapp.palette()
        text = palette.color(QPalette.ColorRole.WindowText)
        assert text.name().lower() == "#ccd6f6"

    def test_sets_base_background_for_surface(self, qapp):
        apply_theme(Theme.EMBER, qapp)
        palette = qapp.palette()
        base = palette.color(QPalette.ColorRole.Base)
        assert base.name() == "#2d1111"

    def test_sets_highlight_accent(self, qapp):
        apply_theme(Theme.ABYSS, qapp)
        palette = qapp.palette()
        highlight = palette.color(QPalette.ColorRole.Highlight)
        assert highlight.name().lower() == "#7b68ee"

    def test_sets_stylesheet_on_app(self, qapp):
        apply_theme(Theme.MIDNIGHT, qapp)
        ss = qapp.styleSheet()
        assert "background-color: #0d0d0d" in ss
        assert "color: #e0e0e0" in ss
