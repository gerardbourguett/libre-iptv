from __future__ import annotations

from src.v2.screens.import_screen import ImportScreen


class TestImportScreenCreation:
    def test_creates_without_error(self, qtbot) -> None:
        screen = ImportScreen()
        qtbot.addWidget(screen)
        assert screen is not None

    def test_default_method_is_file(self, qtbot) -> None:
        screen = ImportScreen()
        qtbot.addWidget(screen)
        assert screen.selected_method() == "file"


class TestImportScreenMethodSelection:
    def test_select_url_method(self, qtbot) -> None:
        screen = ImportScreen()
        qtbot.addWidget(screen)
        screen.select_method("url")
        assert screen.selected_method() == "url"

    def test_select_xtream_method(self, qtbot) -> None:
        screen = ImportScreen()
        qtbot.addWidget(screen)
        screen.select_method("xtream")
        assert screen.selected_method() == "xtream"

    def test_select_file_method(self, qtbot) -> None:
        screen = ImportScreen()
        qtbot.addWidget(screen)
        screen.select_method("url")
        screen.select_method("file")
        assert screen.selected_method() == "file"


class TestImportScreenSignals:
    def test_file_import_emits_request(self, qtbot) -> None:
        screen = ImportScreen()
        qtbot.addWidget(screen)
        received: list[dict] = []
        screen.import_requested.connect(received.append)
        screen._file_input.setText("/tmp/test.m3u")
        screen._trigger_import()
        assert len(received) == 1
        assert received[0]["method"] == "file"
        assert received[0]["path"] == "/tmp/test.m3u"

    def test_url_import_emits_request(self, qtbot) -> None:
        screen = ImportScreen()
        qtbot.addWidget(screen)
        received: list[dict] = []
        screen.import_requested.connect(received.append)
        screen.select_method("url")
        screen._url_input.setText("http://example.com/list.m3u")
        screen._trigger_import()
        assert len(received) == 1
        assert received[0]["method"] == "url"
        assert received[0]["url"] == "http://example.com/list.m3u"

    def test_xtream_import_emits_request(self, qtbot) -> None:
        screen = ImportScreen()
        qtbot.addWidget(screen)
        received: list[dict] = []
        screen.import_requested.connect(received.append)
        screen.select_method("xtream")
        screen._xtream_server.setText("http://myserver.com")
        screen._xtream_user.setText("admin")
        screen._xtream_pass.setText("secret")
        screen._trigger_import()
        assert len(received) == 1
        p = received[0]
        assert p["method"] == "xtream"
        assert p["server"] == "http://myserver.com"
        assert p["username"] == "admin"
        assert p["password"] == "secret"

    def test_cancel_emits_cancelled(self, qtbot) -> None:
        screen = ImportScreen()
        qtbot.addWidget(screen)
        fired: list[bool] = []
        screen.cancelled.connect(lambda: fired.append(True))
        screen._cancel()
        assert fired == [True]

    def test_empty_file_path_does_not_emit(self, qtbot) -> None:
        screen = ImportScreen()
        qtbot.addWidget(screen)
        received: list[dict] = []
        screen.import_requested.connect(received.append)
        screen._file_input.setText("")
        screen._trigger_import()
        assert received == []

    def test_empty_url_does_not_emit(self, qtbot) -> None:
        screen = ImportScreen()
        qtbot.addWidget(screen)
        received: list[dict] = []
        screen.import_requested.connect(received.append)
        screen.select_method("url")
        screen._url_input.setText("  ")
        screen._trigger_import()
        assert received == []


class TestImportScreenStatus:
    def test_set_status_updates_label(self, qtbot) -> None:
        screen = ImportScreen()
        qtbot.addWidget(screen)
        screen.set_status("Importando...")
        assert "Importando" in screen._status_label.text()

    def test_set_progress_visible(self, qtbot) -> None:
        screen = ImportScreen()
        qtbot.addWidget(screen)
        screen.show()
        screen.set_progress(True)
        assert screen._progress_widget.isVisible()

    def test_set_progress_hidden(self, qtbot) -> None:
        screen = ImportScreen()
        qtbot.addWidget(screen)
        screen.set_progress(True)
        screen.set_progress(False)
        assert not screen._progress_widget.isVisible()
