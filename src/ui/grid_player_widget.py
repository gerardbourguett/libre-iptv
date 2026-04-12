from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QGridLayout, QWidget

from src.ui.player_widget import PlayerWidget


class GridPlayerWidget(QWidget):
    active_cell_changed = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._active_cell: int = 0
        self._cells: list[PlayerWidget] = [PlayerWidget() for _ in range(4)]

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for i, (row, col) in enumerate(positions):
            layout.addWidget(self._cells[i], row, col)
            self._cells[i].clicked.connect(lambda idx=i: self._on_cell_clicked(idx))

        self.set_mode(1)
        self._cells[0].set_active(True)

    def set_mode(self, n: int) -> None:
        """Show n cells (1, 2, or 4). Hidden cells stop playback."""
        for i, cell in enumerate(self._cells):
            should_show = i < n
            if not should_show and cell.isVisible():
                cell.stop()
            cell.setVisible(should_show)
        if not self._cells[self._active_cell].isVisible():
            self._active_cell = 0
            self._update_borders()

    def active_player(self) -> PlayerWidget:
        return self._cells[self._active_cell]

    def play_in_active(self, url: str) -> None:
        self._cells[self._active_cell].play(url)

    def stop_active(self) -> None:
        self._cells[self._active_cell].stop()

    def _on_cell_clicked(self, index: int) -> None:
        if self._active_cell == index:
            return
        self._active_cell = index
        self._update_borders()
        self.active_cell_changed.emit(index)

    def _update_borders(self) -> None:
        for i, cell in enumerate(self._cells):
            cell.set_active(i == self._active_cell)
