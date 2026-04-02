import pytest
import sys
import types
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def patch_external_modules(monkeypatch):
    mock_codaio = types.ModuleType("codaio")
    mock_codaio.Coda = MagicMock()
    sys.modules["codaio"] = mock_codaio

    mock_dotenv = types.ModuleType("dotenv")
    mock_dotenv.load_dotenv = MagicMock()
    sys.modules["dotenv"] = mock_dotenv

    yield

    del sys.modules["codaio"]
    del sys.modules["dotenv"]

@patch("os.getenv")
@patch("codaio.Coda")
def test_convert_date_formats_correctly(mock_coda, mock_getenv, patch_external_modules):
    mock_getenv.return_value = "dummy"
    import backend.coda as coda_mod
    year = coda_mod.datetime.now().year
    date_str = "March 15"
    expected = f"{year}-03-15T00:00:00.000-08:00"
    assert coda_mod.convert_date(date_str) == expected


@patch("os.getenv")
@patch("codaio.Coda")
def test_convert_date_cross_year_picks_closest_year(mock_coda, mock_getenv, patch_external_modules, monkeypatch):
    mock_getenv.return_value = "dummy"
    import importlib
    import backend.coda as coda_mod
    importlib.reload(coda_mod)
    
    class FixedDatetime:
        @classmethod
        def now(cls):
            from datetime import datetime as real_datetime
            return real_datetime(2026, 1, 4)

        @staticmethod
        def strptime(date_string, fmt):
            from datetime import datetime as real_datetime
            return real_datetime.strptime(date_string, fmt)

    monkeypatch.setattr(coda_mod, 'datetime', FixedDatetime)
    result = coda_mod.convert_date("December 21")
    assert result.startswith("2025-12-21")

@patch("os.getenv")
@patch("codaio.Coda")
def test_convert_date_invalid_input_raises(mock_coda, mock_getenv, patch_external_modules):
    mock_getenv.return_value = "dummy"
    import backend.coda as coda_mod
    with pytest.raises(ValueError):
        coda_mod.convert_date("NotADate")

@patch("os.getenv")
@patch("codaio.Coda")
def test_get_attendance_filters_and_sorts(mock_coda, mock_getenv, patch_external_modules, monkeypatch):
    mock_getenv.return_value = "dummy"
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

@patch("os.getenv")
@patch("codaio.Coda")
def test_get_attendance_empty(mock_coda, mock_getenv, patch_external_modules, monkeypatch):
    mock_getenv.return_value = "dummy"
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

@patch("os.getenv")
@patch("codaio.Coda")
def test_format_data_returns_attendance_and_count(mock_coda, mock_getenv, patch_external_modules, monkeypatch):
    mock_getenv.return_value = "dummy"
    import importlib
    import backend.coda as coda_mod
    importlib.reload(coda_mod)

    mock_instance = mock_coda.return_value
    mock_instance.list_rows.return_value = {
        "items": [
            {"values": {"Attended": True, "Weekend": "2024-03-15", "BKMS ID": 123}},
            {"values": {"Attended": True, "Weekend": "2024-03-15", "BKMS ID": 456}},
            {"values": {"Attended": False, "Weekend": "2024-03-15", "BKMS ID": 789}},
            {"values": {"Attended": True, "Weekend": "2024-03-15", "BKMS ID": None}},
        ]
    }
    with patch.object(coda_mod, "convert_date", return_value="2024-03-15T00:00:00.000-08:00"):
        result, count = coda_mod.format_data("saturday k1", "March 15")
        assert result == ["123", "456"]
        assert count == 2

@patch("os.getenv")
@patch("codaio.Coda")
def test_format_data_invalid_date_returns_error(mock_coda, mock_getenv, patch_external_modules):
    mock_getenv.return_value = "dummy"
    import backend.coda as coda_mod
    with patch.object(coda_mod, "convert_date", side_effect=ValueError("bad date")):
        result = coda_mod.format_data("saturday k1", "bad date")
        assert "entered the date wrong" in result

@patch("os.getenv")
@patch("codaio.Coda")
def test_format_data_get_attendance_raises_returns_error(mock_coda, mock_getenv, patch_external_modules):
    mock_getenv.return_value = "dummy"
    import backend.coda as coda_mod
    with patch.object(coda_mod, "convert_date", return_value="2024-03-15T00:00:00.000-08:00"):
        with patch.object(coda_mod, "get_attendance", side_effect=Exception("fail")):
            result = coda_mod.format_data("saturday k1", "March 15")
            assert "attendance system is broken" in result.lower()

@patch("os.getenv")
@patch("codaio.Coda")
def test_format_data_all_groups(mock_coda, mock_getenv, patch_external_modules, monkeypatch):
    mock_getenv.return_value = "dummy"
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

@patch("os.getenv")
@patch("codaio.Coda")
def test_format_data_group_case_insensitive(mock_coda, mock_getenv, patch_external_modules, monkeypatch):
    mock_getenv.return_value = "dummy"
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

@patch("os.getenv")
@patch("codaio.Coda")
def test_format_data_attendance_global_reset(mock_coda, mock_getenv, patch_external_modules):
    mock_getenv.return_value = "dummy"
    import backend.coda as coda_mod
    coda_mod.attendance = ["should be cleared"]
    with patch.object(coda_mod, "convert_date", return_value="2024-03-15T00:00:00.000-08:00"):
        with patch.object(coda_mod, "get_attendance") as mock_get_attendance:
            mock_get_attendance.return_value = None
            coda_mod.format_data("saturday k1", "March 15")
            assert coda_mod.attendance == []

@patch("os.getenv")
@patch("codaio.Coda")
def test_env_var_missing_raises(mock_coda, mock_getenv, patch_external_modules, monkeypatch):
    mock_getenv.return_value = None
    import sys
    sys.modules.pop("backend.coda", None)
    with pytest.raises(EnvironmentError):
        import backend.coda


# ── get_goshthi_attendance ────────────────────────────────────────────────────

@patch("os.getenv")
@patch("codaio.Coda")
def test_get_goshthi_attendance_no_rows(mock_coda_cls, mock_getenv, patch_external_modules, monkeypatch):
    mock_getenv.return_value = "dummy"
    import importlib
    import backend.coda as coda_mod
    importlib.reload(coda_mod)

    mock_instance = mock_coda_cls.return_value
    mock_instance.list_rows.return_value = {"items": []}
    coda_mod.attendance = []
    result = coda_mod.get_goshthi_attendance("tbl", 1, "2026")
    assert result is None
    assert coda_mod.attendance == []


@patch("os.getenv")
@patch("codaio.Coda")
def test_get_goshthi_attendance_date_col_by_known_name(mock_coda_cls, mock_getenv, patch_external_modules, monkeypatch):
    mock_getenv.return_value = "dummy"
    import importlib
    import backend.coda as coda_mod
    importlib.reload(coda_mod)

    mock_instance = mock_coda_cls.return_value
    mock_instance.list_rows.return_value = {"items": [
        {"values": {"Month": "2026-01-31T00:00:00.000-05:00", "BKMS ID": 100, "Attended": True}},
        {"values": {"Month": "2026-02-01T00:00:00.000-05:00", "BKMS ID": 200, "Attended": True}},
        {"values": {"Month": "2026-01-15T00:00:00.000-05:00", "BKMS ID": 300, "Attended": False}},
    ]}
    coda_mod.attendance = []
    coda_mod.get_goshthi_attendance("tbl", 1, "2026")
    assert 100 in coda_mod.attendance
    assert 200 not in coda_mod.attendance
    assert 300 not in coda_mod.attendance


@patch("os.getenv")
@patch("codaio.Coda")
def test_get_goshthi_attendance_date_col_by_pattern(mock_coda_cls, mock_getenv, patch_external_modules, monkeypatch):
    mock_getenv.return_value = "dummy"
    import importlib
    import backend.coda as coda_mod
    importlib.reload(coda_mod)

    mock_instance = mock_coda_cls.return_value
    # "CustomDateCol" is NOT a known name; values match M/D/YYYY → pattern detection (lines 69-71)
    mock_instance.list_rows.return_value = {"items": [
        {"values": {"CustomDateCol": "1/31/2026", "BKMS ID": 400, "Attended": True}},
    ]}
    coda_mod.attendance = []
    # Pattern detected but ISO filter won't match "1/31/2026" → no attendance added
    coda_mod.get_goshthi_attendance("tbl", 1, "2026")
    assert 400 not in coda_mod.attendance


@patch("os.getenv")
@patch("codaio.Coda")
def test_get_goshthi_attendance_no_date_col(mock_coda_cls, mock_getenv, patch_external_modules, monkeypatch):
    mock_getenv.return_value = "dummy"
    import importlib
    import backend.coda as coda_mod
    importlib.reload(coda_mod)

    mock_instance = mock_coda_cls.return_value
    mock_instance.list_rows.return_value = {"items": [
        {"values": {"SomeCol": "no-date", "BKMS ID": 500, "Attended": True}},
    ]}
    coda_mod.attendance = []
    result = coda_mod.get_goshthi_attendance("tbl", 1, "2026")
    assert result is None
    assert coda_mod.attendance == []


@patch("os.getenv")
@patch("codaio.Coda")
def test_get_goshthi_attendance_no_bkms_col(mock_coda_cls, mock_getenv, patch_external_modules, monkeypatch):
    mock_getenv.return_value = "dummy"
    import importlib
    import backend.coda as coda_mod
    importlib.reload(coda_mod)

    mock_instance = mock_coda_cls.return_value
    mock_instance.list_rows.return_value = {"items": [
        {"values": {"Month": "2026-01-31T00:00:00.000-05:00", "Attended": True}},
    ]}
    coda_mod.attendance = []
    result = coda_mod.get_goshthi_attendance("tbl", 1, "2026")
    assert result is None


@patch("os.getenv")
@patch("codaio.Coda")
def test_get_goshthi_attendance_no_attended_col(mock_coda_cls, mock_getenv, patch_external_modules, monkeypatch):
    mock_getenv.return_value = "dummy"
    import importlib
    import backend.coda as coda_mod
    importlib.reload(coda_mod)

    mock_instance = mock_coda_cls.return_value
    mock_instance.list_rows.return_value = {"items": [
        {"values": {"Month": "2026-01-31T00:00:00.000-05:00", "BKMS ID": 600}},
    ]}
    coda_mod.attendance = []
    result = coda_mod.get_goshthi_attendance("tbl", 1, "2026")
    assert result is None


@patch("os.getenv")
@patch("codaio.Coda")
def test_get_goshthi_attendance_known_name_variants(mock_coda_cls, mock_getenv, patch_external_modules, monkeypatch):
    """Each known date-column candidate name triggers detection."""
    mock_getenv.return_value = "dummy"
    import importlib
    import backend.coda as coda_mod

    for col_name in ["Weekend", "Date", "Goshthi Date"]:
        importlib.reload(coda_mod)
        mock_instance = mock_coda_cls.return_value
        mock_instance.list_rows.return_value = {"items": [
            {"values": {col_name: "2026-03-15T00:00:00.000-05:00", "BKMS ID": 700, "Attended": True}},
        ]}
        coda_mod.attendance = []
        coda_mod.get_goshthi_attendance("tbl", 3, "2026")
        assert 700 in coda_mod.attendance, f"Failed for col_name={col_name}"


@patch("os.getenv")
@patch("codaio.Coda")
def test_get_goshthi_attendance_drops_nulls(mock_coda_cls, mock_getenv, patch_external_modules, monkeypatch):
    mock_getenv.return_value = "dummy"
    import importlib
    import backend.coda as coda_mod
    importlib.reload(coda_mod)

    mock_instance = mock_coda_cls.return_value
    mock_instance.list_rows.return_value = {"items": [
        {"values": {"Month": "2026-01-15T00:00:00.000-05:00", "BKMS ID": None, "Attended": True}},
        {"values": {"Month": "2026-01-15T00:00:00.000-05:00", "BKMS ID": 800, "Attended": True}},
    ]}
    coda_mod.attendance = []
    coda_mod.get_goshthi_attendance("tbl", 1, "2026")
    assert 800 in coda_mod.attendance
    assert None not in coda_mod.attendance


# ── format_goshthi_data ───────────────────────────────────────────────────────

@patch("os.getenv")
@patch("codaio.Coda")
def test_format_goshthi_data_invalid_month(mock_coda_cls, mock_getenv, patch_external_modules):
    mock_getenv.return_value = "dummy"
    import backend.coda as coda_mod
    result = coda_mod.format_goshthi_data("NotAMonth", "2026")
    assert "Invalid month" in result


@patch("os.getenv")
@patch("codaio.Coda")
def test_format_goshthi_data_returns_unique_sorted_ids(mock_coda_cls, mock_getenv, patch_external_modules, monkeypatch):
    mock_getenv.return_value = "dummy"
    import importlib
    import backend.coda as coda_mod
    importlib.reload(coda_mod)

    monkeypatch.setattr(coda_mod, "goshthi_9_10", "table1")
    monkeypatch.setattr(coda_mod, "goshthi_11_12", None)
    monkeypatch.setattr(coda_mod, "goshthi_college_1_2", None)
    monkeypatch.setattr(coda_mod, "goshthi_college_3_4", None)

    def fake_get_goshthi(table, month_int, year, log=print):
        coda_mod.attendance.extend([500, 200, 500])

    monkeypatch.setattr(coda_mod, "get_goshthi_attendance", fake_get_goshthi)

    result, count = coda_mod.format_goshthi_data("January", "2026")
    assert result == ["200", "500"]
    assert count == 2


@patch("os.getenv")
@patch("codaio.Coda")
def test_format_goshthi_data_skips_none_tables(mock_coda_cls, mock_getenv, patch_external_modules, monkeypatch):
    mock_getenv.return_value = "dummy"
    import importlib
    import backend.coda as coda_mod
    importlib.reload(coda_mod)

    monkeypatch.setattr(coda_mod, "goshthi_9_10", None)
    monkeypatch.setattr(coda_mod, "goshthi_11_12", None)
    monkeypatch.setattr(coda_mod, "goshthi_college_1_2", None)
    monkeypatch.setattr(coda_mod, "goshthi_college_3_4", None)

    called = []
    monkeypatch.setattr(coda_mod, "get_goshthi_attendance", lambda *a, **k: called.append(1))

    result, count = coda_mod.format_goshthi_data("March", "2026")
    assert called == []
    assert count == 0


@patch("os.getenv")
@patch("codaio.Coda")
def test_format_goshthi_data_exception_returns_error(mock_coda_cls, mock_getenv, patch_external_modules, monkeypatch):
    mock_getenv.return_value = "dummy"
    import importlib
    import backend.coda as coda_mod
    importlib.reload(coda_mod)

    monkeypatch.setattr(coda_mod, "goshthi_9_10", "table1")
    monkeypatch.setattr(coda_mod, "goshthi_11_12", None)
    monkeypatch.setattr(coda_mod, "goshthi_college_1_2", None)
    monkeypatch.setattr(coda_mod, "goshthi_college_3_4", None)
    monkeypatch.setattr(coda_mod, "get_goshthi_attendance", lambda *a, **k: (_ for _ in ()).throw(Exception("coda down")))

    result = coda_mod.format_goshthi_data("February", "2026")
    assert "broken" in result.lower()


@patch("os.getenv")
@patch("codaio.Coda")
def test_format_goshthi_data_all_months_valid(mock_coda_cls, mock_getenv, patch_external_modules, monkeypatch):
    mock_getenv.return_value = "dummy"
    import importlib
    import backend.coda as coda_mod
    importlib.reload(coda_mod)

    monkeypatch.setattr(coda_mod, "goshthi_9_10", None)
    monkeypatch.setattr(coda_mod, "goshthi_11_12", None)
    monkeypatch.setattr(coda_mod, "goshthi_college_1_2", None)
    monkeypatch.setattr(coda_mod, "goshthi_college_3_4", None)

    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    for month in months:
        result = coda_mod.format_goshthi_data(month, "2026")
        assert isinstance(result, tuple), f"Expected tuple for month={month}, got {result!r}"


@patch("os.getenv")
@patch("codaio.Coda")
def test_format_goshthi_data_global_attendance_reset(mock_coda_cls, mock_getenv, patch_external_modules, monkeypatch):
    mock_getenv.return_value = "dummy"
    import importlib
    import backend.coda as coda_mod
    importlib.reload(coda_mod)

    coda_mod.attendance = [999]
    monkeypatch.setattr(coda_mod, "goshthi_9_10", None)
    monkeypatch.setattr(coda_mod, "goshthi_11_12", None)
    monkeypatch.setattr(coda_mod, "goshthi_college_1_2", None)
    monkeypatch.setattr(coda_mod, "goshthi_college_3_4", None)

    coda_mod.format_goshthi_data("April", "2026")
    # attendance must be reset at the start of format_goshthi_data
    assert 999 not in coda_mod.attendance


@patch("os.getenv")
@patch("codaio.Coda")
def test_format_goshthi_data_uses_log_callback(mock_coda_cls, mock_getenv, patch_external_modules, monkeypatch):
    mock_getenv.return_value = "dummy"
    import importlib
    import backend.coda as coda_mod
    importlib.reload(coda_mod)

    monkeypatch.setattr(coda_mod, "goshthi_9_10", None)
    monkeypatch.setattr(coda_mod, "goshthi_11_12", None)
    monkeypatch.setattr(coda_mod, "goshthi_college_1_2", None)
    monkeypatch.setattr(coda_mod, "goshthi_college_3_4", None)

    logs = []
    coda_mod.format_goshthi_data("May", "2026", log_callback=lambda msg: logs.append(msg))
    assert any("May" in m for m in logs)