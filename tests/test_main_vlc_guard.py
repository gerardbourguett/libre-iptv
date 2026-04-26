from unittest.mock import patch

import pytest

import main


class TestVlcGuard:
    def test_shows_qmessagebox_and_exits_when_vlc_missing(self):
        with patch("main.QApplication"):
            with patch(
                "main.check_vlc", side_effect=ImportError("VLC not found")
            ):
                with patch("main.QMessageBox") as mock_box:
                    with patch("main.sys.exit") as mock_exit:
                        mock_exit.side_effect = SystemExit(1)
                        with pytest.raises(SystemExit):
                            main.main()
                        mock_box.critical.assert_called_once()
                        mock_exit.assert_called_once_with(1)
