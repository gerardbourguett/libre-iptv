from unittest.mock import MagicMock

import pytest
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import QLabel, QPushButton

from src.ui.about_dialog import AboutDialog


@pytest.fixture
def dialog(qtbot):
    d = AboutDialog()
    qtbot.addWidget(d)
    return d


class TestAboutDialogStructure:
    def test_app_name_label_exists(self, dialog):
        labels = dialog.findChildren(QLabel)
        texts = [lbl.text() for lbl in labels]
        assert any("IPTV Player" in t for t in texts)

    def test_version_label_exists(self, dialog):
        labels = dialog.findChildren(QLabel)
        texts = [lbl.text() for lbl in labels]
        assert any("0.3.0" in t for t in texts)

    def test_description_label_exists(self, dialog):
        labels = dialog.findChildren(QLabel)
        texts = [lbl.text() for lbl in labels]
        assert any("Reproductor de canales IPTV" in t for t in texts)

    def test_license_label_exists(self, dialog):
        labels = dialog.findChildren(QLabel)
        texts = [lbl.text() for lbl in labels]
        assert any("MIT" in t for t in texts)


class TestAboutDialogDonationLinks:
    def test_donation_links_present(self, dialog):
        labels = dialog.findChildren(QLabel)
        texts = [lbl.text() for lbl in labels]
        assert any("GitHub Sponsors" in t for t in texts)
        assert any("Ko-fi" in t for t in texts)

    def test_donation_section_visible(self, dialog):
        labels = dialog.findChildren(QLabel)
        texts = [lbl.text() for lbl in labels]
        assert any("Donar" in t for t in texts) or any(
            "GitHub Sponsors" in t for t in texts
        )

    def test_donation_link_opens_browser(self, dialog, monkeypatch):
        mock_open = MagicMock()
        monkeypatch.setattr("src.ui.about_dialog.QDesktopServices.openUrl", mock_open)

        labels = dialog.findChildren(QLabel)
        link_label = None
        for lbl in labels:
            if "href" in lbl.text():
                link_label = lbl
                break
        assert link_label is not None

        url = "https://github.com/sponsors/gerardbourguett"
        link_label.linkActivated.emit(url)

        mock_open.assert_called_once()
        called_url = mock_open.call_args[0][0]
        assert isinstance(called_url, QUrl)
        assert url in called_url.toString()


class TestAboutDialogBehavior:
    def test_ok_button_exists(self, dialog):
        btn = dialog.findChild(QPushButton)
        assert btn is not None

    def test_ok_button_closes_dialog(self, dialog, qtbot):
        dialog.show()
        btn = dialog.findChild(QPushButton)
        assert btn is not None
        with qtbot.waitSignal(dialog.accepted, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        assert not dialog.isVisible()

    def test_x_button_closes_dialog(self, dialog, qtbot):
        dialog.show()
        assert dialog.isVisible()
        with qtbot.waitSignal(dialog.rejected, timeout=1000):
            dialog.close()
        assert not dialog.isVisible()

    def test_dialog_is_modal(self, dialog):
        assert dialog.isModal()
        assert dialog.windowModality() == Qt.WindowModality.ApplicationModal


class TestAboutDialogTheme:
    def test_dialog_has_dark_theme_styles(self, dialog):
        style = dialog.styleSheet()
        assert "#0d0d0d" in style
        assert "#e0e0e0" in style
        assert "#00bcd4" in style


class TestAboutDialogSpanish:
    def test_all_labels_in_spanish(self, dialog):
        english_words = {"About", "Version", "License", "OK", "Close", "Help", "Donate"}
        for widget in dialog.findChildren((QLabel, QPushButton)):
            text = widget.text()
            for word in english_words:
                assert word.lower() not in text.lower(), (
                    f"Found English word '{word}' in '{text}'"
                )
