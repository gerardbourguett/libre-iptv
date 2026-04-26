from __future__ import annotations

import pytest

from src.v2.dialogs.playlist_dialog import PlaylistDialog


class TestPlaylistDialog:
    def test_dialog_initialises_without_error(self, qtbot):
        dlg = PlaylistDialog()
        qtbot.addWidget(dlg)
        assert dlg.windowTitle() == "Configurar lista M3U"

    def test_url_mode_selected_by_default(self, qtbot):
        dlg = PlaylistDialog()
        qtbot.addWidget(dlg)
        assert dlg._radio_url.isChecked()
        assert not dlg._radio_file.isChecked()

    def test_url_input_enabled_by_default(self, qtbot):
        dlg = PlaylistDialog()
        qtbot.addWidget(dlg)
        assert dlg._url_input.isEnabled()

    def test_browse_button_disabled_by_default(self, qtbot):
        dlg = PlaylistDialog()
        qtbot.addWidget(dlg)
        assert not dlg._browse_btn.isEnabled()

    def test_switching_to_file_mode_enables_browse(self, qtbot):
        dlg = PlaylistDialog()
        qtbot.addWidget(dlg)
        dlg._radio_file.setChecked(True)
        assert dlg._browse_btn.isEnabled()
        assert not dlg._url_input.isEnabled()

    def test_switching_back_to_url_disables_browse(self, qtbot):
        dlg = PlaylistDialog()
        qtbot.addWidget(dlg)
        dlg._radio_file.setChecked(True)
        dlg._radio_url.setChecked(True)
        assert dlg._url_input.isEnabled()
        assert not dlg._browse_btn.isEnabled()

    def test_result_url_populated_on_accept(self, qtbot):
        dlg = PlaylistDialog()
        qtbot.addWidget(dlg)
        dlg._radio_url.setChecked(True)
        dlg._url_input.setText("http://example.com/list.m3u")
        dlg._on_accept()
        assert dlg.result_url == "http://example.com/list.m3u"
        assert dlg.result_path == ""

    def test_empty_url_does_not_accept(self, qtbot):
        dlg = PlaylistDialog()
        qtbot.addWidget(dlg)
        dlg._radio_url.setChecked(True)
        dlg._url_input.setText("   ")
        # _on_accept should NOT call accept() when URL is blank
        initial_result = dlg.result_url
        dlg._on_accept()
        assert dlg.result_url == initial_result  # unchanged; dialog stays open

    def test_result_path_populated_via_file_label(self, qtbot):
        dlg = PlaylistDialog()
        qtbot.addWidget(dlg)
        dlg._radio_file.setChecked(True)
        dlg._file_label.setText("/home/user/lista.m3u")
        dlg._on_accept()
        assert dlg.result_path == "/home/user/lista.m3u"
        assert dlg.result_url == ""

    def test_initial_result_url_is_empty_string(self, qtbot):
        dlg = PlaylistDialog()
        qtbot.addWidget(dlg)
        assert dlg.result_url == ""

    def test_initial_result_path_is_empty_string(self, qtbot):
        dlg = PlaylistDialog()
        qtbot.addWidget(dlg)
        assert dlg.result_path == ""
