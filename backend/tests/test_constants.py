from unittest.mock import patch
import pytest
from backend.utils.constants import (
    SABHA_ROW_MAP, XPATHS, TELEGRAM_GROUP_CONFIG,
    TELEGRAM_GROUP_MENTIONS, BKMS_LOGIN_URL,
    BKMS_REPORT_ATTENDANCE_URL
)

def test_sabha_row_map_structure():
    expected_keys = {"saturday k1", "saturday k2", "sunday k1", "sunday k2"}
    assert set(SABHA_ROW_MAP.keys()) == expected_keys
    assert all(isinstance(v, int) for v in SABHA_ROW_MAP.values())
    assert len(SABHA_ROW_MAP) == 4

def test_sabha_row_map_values():
    assert SABHA_ROW_MAP["saturday k1"] == 1
    assert SABHA_ROW_MAP["saturday k2"] == 2
    assert SABHA_ROW_MAP["sunday k1"] == 3
    assert SABHA_ROW_MAP["sunday k2"] == 4

def test_sabha_row_map_invalid_key():
    with pytest.raises(KeyError):
        _ = SABHA_ROW_MAP["invalid_key"]

def test_xpaths_structure():
    expected_keys = {
        "sabha_wing", "year", "week", "sabha_group",
        "sabha_held_yes", "sabha_held_no", "mark_absent",
        "save_changes"
    }
    assert set(XPATHS.keys()) == expected_keys
    assert all(isinstance(v, str) for v in XPATHS.values())

def test_xpaths_format_strings():
    week_xpath = XPATHS["week"].format(5)
    assert "option[5]" in week_xpath
    
    sabha_group_xpath = XPATHS["sabha_group"].format(3)
    assert "tr[3]" in sabha_group_xpath

@patch('backend.utils.constants.get_config_value')
def test_telegram_group_config_structure(mock_get_config):
    mock_get_config.return_value = "dummy_value"
    
    expected_groups = {"saturday k1", "saturday k2", "sunday k1", "sunday k2"}
    assert set(TELEGRAM_GROUP_CONFIG.keys()) == expected_groups
    
    for group in TELEGRAM_GROUP_CONFIG.values():
        assert "token" in group
        assert "chat_id" in group

def test_telegram_group_mentions_structure():
    assert set(TELEGRAM_GROUP_MENTIONS.keys()) == set(TELEGRAM_GROUP_CONFIG.keys())
    
    for mentions in TELEGRAM_GROUP_MENTIONS.values():
        assert isinstance(mentions, str)
        assert all(word.startswith("@") for word in mentions.split())

def test_telegram_group_mentions_format():
    for group, mentions in TELEGRAM_GROUP_MENTIONS.items():
        assert len(mentions.split()) == 2
        assert all(mention.startswith("@") for mention in mentions.split())

def test_bkms_urls():
    assert BKMS_LOGIN_URL.startswith("https://")
    assert "bk.na.baps.org" in BKMS_LOGIN_URL
    assert BKMS_LOGIN_URL.endswith("ssologin")
    
    assert BKMS_REPORT_ATTENDANCE_URL.startswith("https://")
    assert "bk.na.baps.org" in BKMS_REPORT_ATTENDANCE_URL
    assert "reportweeksabhaattendance" in BKMS_REPORT_ATTENDANCE_URL

@patch('backend.utils.postgresConn.get_config_value')
def test_telegram_config_values(mock_get_config):
    expected_calls = [
        'SAT_K1_TELEGRAM_TOKEN', 'SAT_K1_TELEGRAM_CHAT_ID',
        'SAT_K2_TELEGRAM_TOKEN', 'SAT_K2_TELEGRAM_CHAT_ID',
        'SUN_K1_TELEGRAM_TOKEN', 'SUN_K1_TELEGRAM_CHAT_ID',
        'SUN_K2_TELEGRAM_TOKEN', 'SUN_K2_TELEGRAM_CHAT_ID',
        'MAIN_GROUP_TELEGRAM_TOKEN', 'MAIN_GROUP_TELEGRAM_CHAT_ID'
    ]

    mock_get_config.return_value = "dummy_value"

    import importlib
    import backend.utils.constants as const_mod
    const_mod = importlib.reload(const_mod)

    _ = const_mod.TELEGRAM_GROUP_CONFIG["saturday k1"]["token"]
    _ = const_mod.TELEGRAM_GROUP_CONFIG["saturday k1"]["chat_id"]
    _ = const_mod.TELEGRAM_GROUP_CONFIG["saturday k2"]["token"]
    _ = const_mod.TELEGRAM_GROUP_CONFIG["saturday k2"]["chat_id"]
    _ = const_mod.TELEGRAM_GROUP_CONFIG["sunday k1"]["token"]
    _ = const_mod.TELEGRAM_GROUP_CONFIG["sunday k1"]["chat_id"]
    _ = const_mod.TELEGRAM_GROUP_CONFIG["sunday k2"]["token"]
    _ = const_mod.TELEGRAM_GROUP_CONFIG["sunday k2"]["chat_id"]
    _ = const_mod.MAIN_GROUP_TOKEN
    _ = const_mod.MAIN_GROUP_CHAT_ID

    assert mock_get_config.call_count >= len(expected_calls)
    actual_calls = [call[0][0] for call in mock_get_config.call_args_list]
    for expected_call in expected_calls:
        assert expected_call in actual_calls