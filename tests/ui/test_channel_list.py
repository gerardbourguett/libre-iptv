import pytest
from PyQt6.QtCore import Qt

from src.models.channel import Channel
from src.ui.channel_list import ChannelListPanel, ChannelListWidget


@pytest.fixture
def widget(qtbot):
    w = ChannelListWidget()
    qtbot.addWidget(w)
    return w


@pytest.fixture
def news_sports_channels():
    return [
        Channel(url="http://cnn.com", name="CNN", group="News"),
        Channel(url="http://bbc.com", name="BBC", group="News"),
        Channel(url="http://espn.com", name="ESPN", group="Sports"),
    ]


class TestLoadChannels:
    def test_groups_channels_under_headers(self, widget, news_sports_channels):
        """S1: channels grouped under bold non-selectable headers."""
        widget.load_channels(news_sports_channels)
        # Expected: "News" header, CNN, BBC, "Sports" header, ESPN = 5 items
        assert widget.count() == 5
        news_header = widget.item(0)
        assert news_header.text() == "News"
        assert not (news_header.flags() & Qt.ItemFlag.ItemIsSelectable)

    def test_channels_with_empty_group_go_to_uncategorized(self, widget):
        """S2: channels with group='' appear under 'Uncategorized'."""
        channels = [
            Channel(url="http://a.com", name="Channel A", group=""),
            Channel(url="http://b.com", name="Channel B", group=""),
        ]
        widget.load_channels(channels)
        # "Uncategorized" header + 2 channels = 3 items
        assert widget.count() == 3
        header = widget.item(0)
        assert header.text() == "Uncategorized"
        assert not (header.flags() & Qt.ItemFlag.ItemIsSelectable)

    def test_load_empty_list_clears_widget(self, widget, news_sports_channels):
        """S3: load_channels([]) clears all items."""
        widget.load_channels(news_sports_channels)
        assert widget.count() > 0
        widget.load_channels([])
        assert widget.count() == 0

    def test_channel_item_stores_channel_in_user_role(
        self, widget, news_sports_channels
    ):
        """Channel items store Channel instance in UserRole."""
        widget.load_channels(news_sports_channels)
        # item(1) is first channel after "News" header
        channel_item = widget.item(1)
        stored = channel_item.data(Qt.ItemDataRole.UserRole)
        assert isinstance(stored, Channel)
        assert stored.name == "CNN"


class TestChannelSelectedSignal:
    def test_click_channel_item_emits_signal(self, widget, qtbot, news_sports_channels):
        """S4: clicking a channel item emits channel_selected with correct Channel."""
        widget.load_channels(news_sports_channels)
        channel_item = widget.item(1)  # CNN (after "News" header)

        with qtbot.waitSignal(widget.channel_selected, timeout=1000) as blocker:
            widget.itemClicked.emit(channel_item)

        emitted: Channel = blocker.args[0]
        assert emitted.name == "CNN"
        assert emitted.url == "http://cnn.com"

    def test_click_group_header_does_not_emit_signal(
        self, widget, qtbot, news_sports_channels
    ):
        """S5: clicking a group header does NOT emit channel_selected."""
        widget.load_channels(news_sports_channels)
        header_item = widget.item(0)  # "News" header

        signal_received = []
        widget.channel_selected.connect(lambda ch: signal_received.append(ch))
        widget.itemClicked.emit(header_item)

        assert signal_received == []


class TestFilterChannels:
    def test_filter_hides_non_matching_channels(self, widget, news_sports_channels):
        widget.load_channels(news_sports_channels)
        widget.filter_channels("ESPN")
        # item(0)=News header, item(1)=CNN, item(2)=BBC
        # item(3)=Sports header, item(4)=ESPN
        cnn_item = widget.item(1)  # CNN
        assert cnn_item.isHidden()

    def test_filter_shows_matching_channels(self, widget, news_sports_channels):
        widget.load_channels(news_sports_channels)
        widget.filter_channels("ESPN")
        espn_item = widget.item(4)  # ESPN
        assert not espn_item.isHidden()

    def test_filter_hides_header_when_all_channels_hidden(
        self, widget, news_sports_channels
    ):
        widget.load_channels(news_sports_channels)
        widget.filter_channels("ESPN")
        news_header = widget.item(0)  # "News" header — no matches under it
        assert news_header.isHidden()

    def test_filter_shows_header_when_at_least_one_channel_matches(
        self, widget, news_sports_channels
    ):
        widget.load_channels(news_sports_channels)
        widget.filter_channels("ESPN")
        sports_header = widget.item(3)  # "Sports" header — ESPN matches
        assert not sports_header.isHidden()

    def test_filter_empty_string_shows_all(self, widget, news_sports_channels):
        widget.load_channels(news_sports_channels)
        widget.filter_channels("ESPN")
        widget.filter_channels("")  # clear
        for i in range(widget.count()):
            assert not widget.item(i).isHidden()

    def test_filter_case_insensitive(self, widget, news_sports_channels):
        widget.load_channels(news_sports_channels)
        widget.filter_channels("cnn")  # lowercase
        cnn_item = widget.item(1)
        assert not cnn_item.isHidden()


class TestChannelListPanel:
    @pytest.fixture
    def panel(self, qtbot):
        p = ChannelListPanel()
        qtbot.addWidget(p)
        return p

    def test_panel_has_search_bar(self, panel):
        from PyQt6.QtWidgets import QLineEdit
        search = panel.findChild(QLineEdit)
        assert search is not None

    def test_panel_exposes_channel_list(self, panel):
        assert isinstance(panel.channel_list, ChannelListWidget)

    def test_panel_channel_selected_signal_accessible(self, panel):
        assert hasattr(panel.channel_list, "channel_selected")

    def test_typing_in_search_filters_channels(
        self, panel, qtbot, news_sports_channels
    ):
        panel.channel_list.load_channels(news_sports_channels)
        from PyQt6.QtWidgets import QLineEdit
        search = panel.findChild(QLineEdit)
        search.setText("ESPN")
        # CNN should be hidden (item(1) after News header)
        cnn_item = panel.channel_list.item(1)
        assert cnn_item.isHidden()
