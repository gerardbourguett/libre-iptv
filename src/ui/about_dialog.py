import importlib.metadata

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDesktopServices, QFont
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QWidget

from src.i18n import t

_DONATION_LINKS: dict[str, str] = {
    "GitHub Sponsors": "https://github.com/sponsors/gerardbourguett",
    "Ko-fi": "https://ko-fi.com/vanderfondi",
}

try:
    _VERSION = importlib.metadata.version("iptv")
except importlib.metadata.PackageNotFoundError:
    _VERSION = "0.2.0"

_DIALOG_STYLE = """
QDialog {
    background: #0d0d0d;
}
QLabel {
    color: #e0e0e0;
}
QPushButton#ok_btn {
    background: #00bcd4;
    color: #000000;
    border: none;
    border-radius: 6px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: bold;
}
QPushButton#ok_btn:hover {
    background: #00e5ff;
}
"""


class AboutDialog(QDialog):
    """Modal dialog showing app metadata and donation links."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("about.title"))
        self.setMinimumWidth(400)
        self.setModal(True)
        self.setStyleSheet(_DIALOG_STYLE)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(32, 32, 32, 32)

        # App name
        name_label = QLabel(t("about.app_name"))
        name_label.setFont(QFont("", 18, QFont.Weight.Bold))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        # Version
        version_label = QLabel(t("about.version", version=_VERSION))
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        # Description
        desc_label = QLabel(t("about.description"))
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # License
        license_label = QLabel(t("about.license"))
        license_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(license_label)

        # Spacer
        spacer = QWidget()
        spacer.setMinimumHeight(12)
        layout.addWidget(spacer)

        # Donation section
        donate_title = QLabel(t("about.donate"))
        donate_title.setFont(QFont("", 12, QFont.Weight.Bold))
        donate_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(donate_title)

        for label_text, url in _DONATION_LINKS.items():
            link_label = QLabel(f"<a href='{url}'>{label_text}</a>")
            link_label.setTextFormat(Qt.TextFormat.RichText)
            link_label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextBrowserInteraction
            )
            link_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            link_label.linkActivated.connect(self._open_url)
            layout.addWidget(link_label)

        # Spacer
        layout.addStretch()

        # OK button
        ok_btn = QPushButton(t("about.ok_button"))
        ok_btn.setObjectName("ok_btn")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def _open_url(self, url: str) -> None:
        from PyQt6.QtCore import QUrl

        QDesktopServices.openUrl(QUrl(url))
