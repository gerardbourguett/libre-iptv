import sys

from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import QApplication

from src.profiles.manager import ProfileManager
from src.ui.main_window import MainWindow
from src.ui.profile_chooser import ProfileChooserDialog


def configure_app(app: QApplication) -> None:
    """Apply Fusion dark theme and typography to the application."""
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#0d0d0d"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#e0e0e0"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#161616"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#1e1e1e"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#e0e0e0"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#1e1e1e"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#e0e0e0"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#00bcd4"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
    palette.setColor(QPalette.ColorRole.Mid, QColor("#2a2a2a"))
    palette.setColor(QPalette.ColorRole.Dark, QColor("#0a0a0a"))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#555555"))
    app.setPalette(palette)

    font = QFont("Segoe UI", 10)
    app.setFont(font)


def main() -> None:
    app = QApplication(sys.argv)
    app.setOrganizationName("iptv")
    app.setApplicationName("iptv-player")
    configure_app(app)

    manager = ProfileManager()

    chooser = ProfileChooserDialog(manager)
    chooser.exec()

    window = MainWindow(manager)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
