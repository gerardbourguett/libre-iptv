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
        assert "▼" in news_header.text() and "News" in news_header.text()
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
        assert "▼" in header.text() and "Uncategorized" in header.text()
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


class TestCollapsibleGroups:
    @pytest.fixture
    def news_widget(self, qtbot):
        w = ChannelListWidget()
        qtbot.addWidget(w)
        channels = [
            Channel(url="http://cnn.com", name="CNN", group="News"),
            Channel(url="http://bbc.com", name="BBC", group="News"),
        ]
        w.load_channels(channels)
        return w

    def test_header_starts_expanded(self, news_widget):
        """Groups start expanded with ▼ arrow indicator."""
        header = news_widget.item(0)
        assert "▼" in header.text()
        assert not news_widget.item(1).isHidden()

    def test_header_text_includes_count(self, news_widget):
        """Header shows arrow, group name, and channel count."""
        header = news_widget.item(0)
        assert "▼ News (2)" in header.text()

    def test_click_header_collapses_group(self, news_widget):
        """Clicking an expanded header hides channels but keeps the header visible."""
        header = news_widget.item(0)
        news_widget.itemClicked.emit(header)
        assert "▶" in header.text()
        assert news_widget.item(1).isHidden()
        assert not header.isHidden()  # header must remain visible to allow re-expansion

    def test_click_collapsed_header_expands(self, news_widget):
        """Clicking a collapsed header shows its channels and flips arrow to ▼."""
        header = news_widget.item(0)
        news_widget.itemClicked.emit(header)  # collapse
        news_widget.itemClicked.emit(header)  # expand
        assert "▼" in header.text()
        assert not news_widget.item(1).isHidden()

    def test_search_shows_channels_in_collapsed_group(self, news_widget):
        """Search query overrides collapse — matching channels become visible."""
        header = news_widget.item(0)
        news_widget.itemClicked.emit(header)  # collapse group
        news_widget.filter_channels("CNN")
        assert not news_widget.item(1).isHidden()  # CNN visible despite collapse

    def test_clear_search_restores_collapse(self, news_widget):
        """Clearing the search restores collapsed groups to hidden."""
        header = news_widget.item(0)
        news_widget.itemClicked.emit(header)   # collapse
        news_widget.filter_channels("CNN")     # override
        news_widget.filter_channels("")        # clear
        assert news_widget.item(1).isHidden()  # back to collapsed

    def test_load_resets_collapse_state(self, news_widget):
        """Loading new channels resets all collapse state to expanded."""
        header = news_widget.item(0)
        news_widget.itemClicked.emit(header)  # collapse
        channels = [
            Channel(url="http://cnn.com", name="CNN", group="News"),
            Channel(url="http://bbc.com", name="BBC", group="News"),
        ]
        news_widget.load_channels(channels)
        new_header = news_widget.item(0)
        assert "▼" in new_header.text()
        assert not news_widget.item(1).isHidden()


class TestChannelListStyling:
    def test_widget_has_stylesheet(self, widget):
        """ChannelListWidget applies a stylesheet."""
        assert len(widget.styleSheet()) > 0

    def test_search_focus_uses_cyan_accent(self, qtbot):
        """Search bar focus border uses the cyan accent color."""
        panel = ChannelListPanel()
        qtbot.addWidget(panel)
        from PyQt6.QtWidgets import QLineEdit
        search = panel.findChild(QLineEdit)
        assert "00bcd4" in search.styleSheet()

    def test_header_has_muted_foreground(self, widget, news_sports_channels):
        """Category headers use muted grey foreground #9e9e9e."""
        widget.load_channels(news_sports_channels)
        header = widget.item(0)
        assert header.foreground().color().name() == "#9e9e9e"

    def test_channel_item_has_indent(self, widget, news_sports_channels):
        """Channel items have a leading 2-space indent."""
        widget.load_channels(news_sports_channels)
        channel_item = widget.item(1)  # CNN after News header
        assert channel_item.text().startswith("  ")


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
