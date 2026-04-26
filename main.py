import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QCursor, QFont, QPalette
from PyQt6.QtWidgets import QApplication, QMessageBox

from src.i18n import init_translator
from src.platform import check_vlc, get_platform_font
from src.profiles.manager import ProfileManager
from src.ui.app_settings import AppSettings
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

    font = QFont(get_platform_font(), 10)
    app.setFont(font)


def main() -> None:
    app = QApplication(sys.argv)
    app.setOrganizationName("iptv")
    app.setApplicationName("iptv-player")
    configure_app(app)

    try:
        check_vlc()
    except ImportError as exc:
        QMessageBox.critical(None, "VLC Not Found", str(exc))
        sys.exit(1)

    settings = AppSettings()
    init_translator(settings=settings)

    manager = ProfileManager()

    chooser = ProfileChooserDialog(manager)
    chooser.exec()
    # On Windows, closing a modal dialog that contained a widget with
    # PointingHandCursor can leave the cursor "stuck" until the next
    # mouseMoveEvent. Push + immediately pop an override to force a reset.
    QApplication.setOverrideCursor(QCursor(Qt.CursorShape.ArrowCursor))
    QApplication.restoreOverrideCursor()

    window = MainWindow(manager)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
