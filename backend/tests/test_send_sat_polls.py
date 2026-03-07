import pytest
from unittest.mock import patch
from backend.send_sat_polls import main


class TestSendSatPolls:
    @patch("backend.send_sat_polls.send_polls_to_targets")
    @patch("backend.send_sat_polls.build_targets_from_env")
    def test_main(self, mock_build_targets, mock_send_polls):
        mock_targets = ["target1", "target2"]
        mock_build_targets.return_value = mock_targets

        main()

        mock_build_targets.assert_called_once_with("SAT_")

        mock_send_polls.assert_called_once_with(mock_targets, for_prefix="SAT_")

    def test_main_block(self):
        import sys
        import runpy
        sys.modules.pop("backend.send_sat_polls", None)
        with patch("backend.utils.common_polls.build_targets_from_env", return_value=[]) as mock_build, \
             patch("backend.utils.common_polls.send_polls_to_targets") as mock_send:
            runpy.run_module("backend.send_sat_polls", run_name="__main__", alter_sys=True)
        mock_build.assert_called_once_with("SAT_")
        mock_send.assert_called_once_with([], for_prefix="SAT_")