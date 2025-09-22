import pytest
import sys
import types
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def patch_external_modules(monkeypatch):
    mock_codaio = types.ModuleType("codaio")
    mock_codaio.Coda = MagicMock()
    sys.modules["codaio"] = mock_codaio
    yield
    del sys.modules["codaio"]

@pytest.fixture
def mock_db_config():
    return {
        "CODA_API_KEY": "dummy-api-key",
        "CODA_DOC_ID": "dummy-doc-id",
        "SATURDAY_K1_TABLE_ID": "sat-k1-table",
        "SATURDAY_K2_TABLE_ID": "sat-k2-table",
        "SUNDAY_K1_TABLE_ID": "sun-k1-table",
        "SUNDAY_K2_TABLE_ID": "sun-k2-table"
    }

@patch("backend.utils.postgresConn.get_config_value")
@patch("codaio.Coda")
def test_convert_date_formats_correctly(mock_coda, mock_get_config, patch_external_modules, mock_db_config):
    mock_get_config.side_effect = mock_db_config.get
    import backend.coda as coda_mod
    year = coda_mod.datetime.now().year
    date_str = "March 15"
    expected = f"{year}-03-15T00:00:00.000-08:00"
    assert coda_mod.convert_date(date_str) == expected

@patch("backend.utils.postgresConn.get_config_value")
@patch("codaio.Coda")
def test_convert_date_invalid_input_raises(mock_coda, mock_get_config, patch_external_modules, mock_db_config):
    mock_get_config.side_effect = mock_db_config.get
    import backend.coda as coda_mod
    with pytest.raises(ValueError):
        coda_mod.convert_date("NotADate")

@patch("backend.utils.postgresConn.get_config_value")
@patch("codaio.Coda")
def test_get_attendance_filters_and_sorts(mock_coda, mock_get_config, patch_external_modules, mock_db_config):
    mock_get_config.side_effect = mock_db_config.get
    import importlib
    import backend.coda as coda_mod
    importlib.reload(coda_mod)

    mock_instance = mock_coda.return_value
    mock_instance.list_rows.return_value = {
        "items": [
            {"values": {"Attended": True, "Weekend": "2024-03-15", "BKMS ID": 456}},
            {"values": {"Attended": True, "Weekend": "2024-03-15", "BKMS ID": 123}},
            {"values": {"Attended": False, "Weekend": "2024-03-15", "BKMS ID": 789}},
            {"values": {"Attended": True, "Weekend": "2024-03-15", "BKMS ID": None}},
        ]
    }
    coda_mod.attendance = []
    coda_mod.get_attendance("dummy-table-id", "2024-03-15T00:00:00.000-08:00")
    assert coda_mod.attendance == ["123", "456"]

@patch("backend.utils.postgresConn.get_config_value")
@patch("codaio.Coda")
def test_get_attendance_empty(mock_coda, mock_get_config, patch_external_modules, monkeypatch, mock_db_config):
    mock_get_config.side_effect = mock_db_config.get
    import importlib
    import backend.coda as coda_mod
    importlib.reload(coda_mod)

    mock_instance = mock_coda.return_value
    mock_instance.list_rows.return_value = {"items": []}
    import pandas as pd
    original_df = pd.DataFrame
    def fake_df(*args, **kwargs):
        return original_df([], columns=["Attended", "Weekend", "BKMS ID"])
    monkeypatch.setattr(pd, "DataFrame", fake_df)
    coda_mod.attendance = []
    result = coda_mod.get_attendance("dummy-table-id", "2024-03-15T00:00:00.000-08:00")
    assert coda_mod.attendance == []
    assert result is None

@patch("backend.utils.postgresConn.get_config_value")
@patch("codaio.Coda")
def test_format_data_returns_attendance_and_count(mock_coda, mock_get_config, patch_external_modules, monkeypatch, mock_db_config):
    mock_get_config.side_effect = mock_db_config.get
    import importlib
    import backend.coda as coda_mod
    importlib.reload(coda_mod)

    mock_instance = mock_coda.return_value
    mock_instance.list_rows.return_value = {
        "items": [
            {"values": {"Attended": True, "Weekend": "2024-03-15", "BKMS ID": 123}},
            {"values": {"Attended": True, "Weekend": "2024-03-15", "BKMS ID": 456}},
        ]
    }
    with patch.object(coda_mod, "convert_date", return_value="2024-03-15T00:00:00.000-08:00"):
        result, count = coda_mod.format_data("saturday k1", "March 15")
        assert result == ["123", "456"]
        assert count == 2

@patch("backend.utils.postgresConn.get_config_value")
@patch("codaio.Coda")
def test_format_data_invalid_date_returns_error(mock_coda, mock_get_config, patch_external_modules, mock_db_config):
    mock_get_config.side_effect = mock_db_config.get
    import backend.coda as coda_mod
    with patch.object(coda_mod, "convert_date", side_effect=ValueError("bad date")):
        result = coda_mod.format_data("saturday k1", "bad date")
        assert "entered the date wrong" in result

@patch("backend.utils.postgresConn.get_config_value")
@patch("codaio.Coda")
def test_format_data_get_attendance_raises_returns_error(mock_coda, mock_get_config, patch_external_modules, mock_db_config):
    mock_get_config.side_effect = mock_db_config.get
    import backend.coda as coda_mod
    with patch.object(coda_mod, "convert_date", return_value="2024-03-15T00:00:00.000-08:00"):
        with patch.object(coda_mod, "get_attendance", side_effect=Exception("fail")):
            result = coda_mod.format_data("saturday k1", "March 15")
            assert "attendance system is broken" in result.lower()

@patch("backend.utils.postgresConn.get_config_value")
@patch("codaio.Coda")
def test_format_data_all_groups(mock_coda, mock_get_config, patch_external_modules, monkeypatch, mock_db_config):
    mock_get_config.side_effect = mock_db_config.get
    import importlib
    import backend.coda as coda_mod
    importlib.reload(coda_mod)
    mock_instance = mock_coda.return_value
    mock_instance.list_rows.return_value = {
        "items": [
            {"values": {"Attended": True, "Weekend": "2024-03-15", "BKMS ID": 1}},
        ]
    }
    with patch.object(coda_mod, "convert_date", return_value="2024-03-15T00:00:00.000-08:00"):
        for group in ["saturday k1", "saturday k2", "sunday k1", "sunday k2"]:
            result, count = coda_mod.format_data(group, "March 15")
            assert result == ["1"]
            assert count == 1

@patch("backend.utils.postgresConn.get_config_value")
@patch("codaio.Coda")
def test_format_data_group_case_insensitive(mock_coda, mock_get_config, patch_external_modules, monkeypatch, mock_db_config):
    mock_get_config.side_effect = mock_db_config.get
    import importlib
    import backend.coda as coda_mod
    importlib.reload(coda_mod)
    mock_instance = mock_coda.return_value
    mock_instance.list_rows.return_value = {
        "items": [
            {"values": {"Attended": True, "Weekend": "2024-03-15", "BKMS ID": 2}},
        ]
    }
    with patch.object(coda_mod, "convert_date", return_value="2024-03-15T00:00:00.000-08:00"):
        result, count = coda_mod.format_data("SaturDay K1", "March 15")
        assert result == ["2"]
        assert count == 1

@patch("backend.utils.postgresConn.get_config_value")
@patch("codaio.Coda")
def test_format_data_attendance_global_reset(mock_coda, mock_get_config, patch_external_modules, mock_db_config):
    mock_get_config.side_effect = mock_db_config.get
    import backend.coda as coda_mod
    coda_mod.attendance = ["should be cleared"]
    with patch.object(coda_mod, "convert_date", return_value="2024-03-15T00:00:00.000-08:00"):
        with patch.object(coda_mod, "get_attendance") as mock_get_attendance:
            mock_get_attendance.return_value = None
            coda_mod.format_data("saturday k1", "March 15")
            assert coda_mod.attendance == []

@patch("backend.utils.postgresConn.get_config_value")
@patch("codaio.Coda")
def test_config_missing_raises(mock_coda, mock_get_config, patch_external_modules):
    mock_get_config.return_value = None
    import sys
    sys.modules.pop("backend.coda", None)
    with pytest.raises(OSError, match="CODA_API_KEY is not set in database"):
        import backend.coda