from unittest.mock import MagicMock, patch

import pytest

from src.ui.grid_player_widget import GridPlayerWidget


@pytest.fixture
def mock_vlc():
    with patch("src.ui.player_widget.vlc") as mock:
        instance = MagicMock()
        player = MagicMock()
        mock.Instance.return_value = instance
        instance.media_player_new.return_value = player
        yield mock, player


@pytest.fixture
def grid(qtbot, mock_vlc):
    w = GridPlayerWidget()
    qtbot.addWidget(w)
    w.show()
    return w


class TestGridLayout:
    def test_mode_1_shows_one_cell(self, grid):
        """Single mode: only the first cell is visible."""
        grid.set_mode(1)
        assert grid._cells[0].isVisible()
        assert not grid._cells[1].isVisible()
        assert not grid._cells[2].isVisible()
        assert not grid._cells[3].isVisible()

    def test_mode_2_shows_two_cells(self, grid):
        """Dual mode: first two cells are visible."""
        grid.set_mode(2)
        assert grid._cells[0].isVisible()
        assert grid._cells[1].isVisible()
        assert not grid._cells[2].isVisible()
        assert not grid._cells[3].isVisible()

    def test_mode_4_shows_four_cells(self, grid):
        """Quad mode: all four cells are visible."""
        grid.set_mode(4)
        for cell in grid._cells:
            assert cell.isVisible()

    def test_default_mode_is_1(self, grid):
        """Grid starts in single mode."""
        assert not grid._cells[1].isVisible()


class TestActiveCell:
    def test_initial_active_cell_is_0(self, grid):
        """Active cell starts at index 0."""
        assert grid._active_cell == 0

    def test_click_cell_changes_active(self, grid, qtbot):
        """Clicking a cell updates _active_cell."""
        grid.set_mode(2)
        grid._on_cell_clicked(1)
        assert grid._active_cell == 1

    def test_active_cell_changed_signal_emitted(self, grid, qtbot):
        """Clicking a cell emits active_cell_changed with the new index."""
        grid.set_mode(2)
        with qtbot.waitSignal(grid.active_cell_changed, timeout=500) as blocker:
            grid._on_cell_clicked(1)
        assert blocker.args[0] == 1

    def test_active_player_returns_correct_widget(self, grid):
        """active_player() returns the PlayerWidget at the active cell."""
        grid._active_cell = 0
        assert grid.active_player() is grid._cells[0]


class TestPlayRouting:
    def test_play_in_active_delegates_to_active_cell(self, grid, mock_vlc):
        """play_in_active(url) calls play() on the active PlayerWidget."""
        _, player = mock_vlc
        grid._active_cell = 0
        grid.play_in_active("http://stream.example.com/test")
        player.set_media.assert_called_once()
        player.play.assert_called_once()
