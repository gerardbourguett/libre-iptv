from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication


@dataclass(frozen=True)
class ThemeColors:
    background: str
    surface: str
    text: str
    accent: str


class Theme(Enum):
    MIDNIGHT = ThemeColors("#0d0d0d", "#1e1e1e", "#e0e0e0", "#00bcd4")
    OCEAN = ThemeColors("#0a192f", "#112240", "#ccd6f6", "#64ffda")
    EMBER = ThemeColors("#1a0a0a", "#2d1111", "#e0d0c0", "#ff6b35")
    ABYSS = ThemeColors("#0a0a1a", "#141428", "#b8c0cc", "#7b68ee")


def apply_theme(theme: Theme, app: QApplication) -> None:
    colors = theme.value
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(colors.background))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(colors.text))
    palette.setColor(QPalette.ColorRole.Base, QColor(colors.surface))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors.surface))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors.surface))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors.text))
    palette.setColor(QPalette.ColorRole.Text, QColor(colors.text))
    palette.setColor(QPalette.ColorRole.Button, QColor(colors.surface))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors.text))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(colors.accent))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors.background))
    app.setPalette(palette)
    app.setStyleSheet(
        f"QWidget {{ background-color: {colors.background}; color: {colors.text}; }}\n"
        f"QLineEdit {{ background-color: {colors.surface}; color: {colors.text}; "
        f"border: 1px solid {colors.accent}; }}\n"
        f"QListWidget {{ background-color: {colors.surface}; color: {colors.text}; }}\n"
        f"QScrollArea {{ background-color: {colors.background}; }}\n"
        f"QFrame {{ background-color: {colors.surface}; }}\n"
    )
