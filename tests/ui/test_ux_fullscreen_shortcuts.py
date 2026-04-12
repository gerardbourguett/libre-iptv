import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QApplication

from src.models.profile import AVATAR_COLORS
from src.profiles.manager import ProfileManager
from src.ui.main_window import MainWindow


@pytest.fixture
def manager(tmp_path):
    mgr = ProfileManager(base_dir=tmp_path)
    mgr.create_profile("Test", AVATAR_COLORS[0])
    return mgr


@pytest.fixture
def window(manager, qtbot):
    w = MainWindow(manager)
    qtbot.addWidget(w)
    w.show()
    return w


def _key_event(key: Qt.Key, text: str = "") -> QKeyEvent:
    return QKeyEvent(QKeyEvent.Type.KeyPress, key, Qt.KeyboardModifier.NoModifier, text)


def _process() -> None:
    QApplication.processEvents()


class TestFullscreen:
    def test_f11_enters_fullscreen(self, window, qtbot):
        assert not window._fullscreen
        window.keyPressEvent(_key_event(Qt.Key.Key_F11))
        assert window._fullscreen

    def test_f11_again_exits_fullscreen(self, window, qtbot):
        window.keyPressEvent(_key_event(Qt.Key.Key_F11))
        window.keyPressEvent(_key_event(Qt.Key.Key_F11))
        assert not window._fullscreen

    def test_escape_exits_fullscreen(self, window, qtbot):
        window.keyPressEvent(_key_event(Qt.Key.Key_F11))
        assert window._fullscreen
        window.keyPressEvent(_key_event(Qt.Key.Key_Escape))
        assert not window._fullscreen

    def test_escape_does_nothing_when_not_fullscreen(self, window, qtbot):
        assert not window._fullscreen
        window.keyPressEvent(_key_event(Qt.Key.Key_Escape))
        assert not window._fullscreen


class TestLayoutShortcuts:
    def test_key_1_sets_single_layout(self, window, qtbot):
        window.keyPressEvent(_key_event(Qt.Key.Key_2, "2"))
        window.keyPressEvent(_key_event(Qt.Key.Key_1, "1"))
        assert window._layout_buttons[1].isChecked()
        assert not window._layout_buttons[2].isChecked()

    def test_key_2_sets_dual_layout(self, window, qtbot):
        window.keyPressEvent(_key_event(Qt.Key.Key_2, "2"))
        assert window._layout_buttons[2].isChecked()

    def test_key_4_sets_quad_layout(self, window, qtbot):
        window.keyPressEvent(_key_event(Qt.Key.Key_4, "4"))
        assert window._layout_buttons[4].isChecked()
