import pytest

from src.ui.loading_overlay import LoadingOverlay


class TestLoadingOverlay:
    def test_show_loading_makes_overlay_visible(self, qtbot):
        """S1: show_loading() makes the overlay visible."""
        overlay = LoadingOverlay()
        qtbot.addWidget(overlay)
        overlay.show_loading("Cargando canales…")
        assert overlay.isVisible()

    def test_hide_loading_makes_overlay_hidden(self, qtbot):
        """S2: hide_loading() makes the overlay hidden."""
        overlay = LoadingOverlay()
        qtbot.addWidget(overlay)
        overlay.show_loading("Cargando canales…")
        overlay.hide_loading()
        assert overlay.isHidden()

    def test_show_loading_sets_label_text(self, qtbot):
        """S3: show_loading(text) updates the displayed text."""
        overlay = LoadingOverlay()
        qtbot.addWidget(overlay)
        overlay.show_loading("Cargando canales…")
        assert overlay._label.text() == "Cargando canales…"

    def test_default_text_on_show_loading(self, qtbot):
        """S4: show_loading() without arguments uses default Spanish text."""
        overlay = LoadingOverlay()
        qtbot.addWidget(overlay)
        overlay.show_loading()
        assert "Cargando" in overlay._label.text()
