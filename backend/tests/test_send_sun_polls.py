import pytest
from unittest.mock import patch
from backend.send_sun_polls import main


class TestSendSunPolls:
    @patch("backend.send_sun_polls.send_polls_to_targets")
    @patch("backend.send_sun_polls.build_targets_from_env")
    def test_main(self, mock_build_targets, mock_send_polls):
        mock_targets = ["target1", "target2"]
        mock_build_targets.return_value = mock_targets

        main()

        mock_build_targets.assert_called_once_with("SUN_")

        mock_send_polls.assert_called_once_with(mock_targets, for_prefix="SUN_")