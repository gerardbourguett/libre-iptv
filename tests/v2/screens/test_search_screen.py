from __future__ import annotations

from src.models.channel import Channel
from src.v2.screens.search_screen import SearchScreen


def _ch(name: str) -> Channel:
    return Channel(url=f"http://example.com/{name}", name=name)


class TestSearchScreenCreation:
    def test_creates_without_error(self, qtbot) -> None:
        screen = SearchScreen()
        qtbot.addWidget(screen)
        assert screen is not None

    def test_result_count_zero_by_default(self, qtbot) -> None:
        screen = SearchScreen()
        qtbot.addWidget(screen)
        assert screen.result_count() == 0


class TestSearchScreenFilter:
    def test_set_query_filters_by_name(self, qtbot) -> None:
        channels = [_ch("CNN"), _ch("BBC"), _ch("ESPN")]
        screen = SearchScreen()
        qtbot.addWidget(screen)
        screen.load_channels(channels)
        screen.set_query("CNN")
        assert screen.result_count() == 1

    def test_set_query_case_insensitive(self, qtbot) -> None:
        screen = SearchScreen()
        qtbot.addWidget(screen)
        screen.load_channels([_ch("CNN"), _ch("BBC")])
        screen.set_query("cnn")
        assert screen.result_count() == 1

    def test_partial_match_returns_results(self, qtbot) -> None:
        screen = SearchScreen()
        qtbot.addWidget(screen)
        screen.load_channels([_ch("CNN International"), _ch("BBC"), _ch("CNN en Español")])
        screen.set_query("CNN")
        assert screen.result_count() == 2

    def test_no_match_returns_zero(self, qtbot) -> None:
        screen = SearchScreen()
        qtbot.addWidget(screen)
        screen.load_channels([_ch("CNN"), _ch("BBC")])
        screen.set_query("ZZZ_NO_MATCH")
        assert screen.result_count() == 0

    def test_empty_query_clears_results(self, qtbot) -> None:
        screen = SearchScreen()
        qtbot.addWidget(screen)
        screen.load_channels([_ch("CNN"), _ch("BBC")])
        screen.set_query("CNN")
        screen.set_query("")
        assert screen.result_count() == 0

    def test_load_channels_resets_results(self, qtbot) -> None:
        screen = SearchScreen()
        qtbot.addWidget(screen)
        screen.load_channels([_ch("CNN")])
        screen.set_query("CNN")
        assert screen.result_count() == 1
        screen.load_channels([_ch("BBC"), _ch("ESPN")])
        assert screen.result_count() == 0


class TestSearchScreenSignal:
    def test_channel_selected_on_item_click(self, qtbot) -> None:
        channels = [_ch("CNN"), _ch("BBC")]
        screen = SearchScreen()
        qtbot.addWidget(screen)
        screen.load_channels(channels)
        screen.set_query("CNN")
        received: list[Channel] = []
        screen.channel_selected.connect(received.append)
        screen._results_list.itemClicked.emit(screen._results_list.item(0))
        assert len(received) == 1
        assert received[0].name == "CNN"
