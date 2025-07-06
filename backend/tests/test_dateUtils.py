import pytest
from datetime import datetime, timedelta
from backend.utils import dateUtils

class FixedDatetime(datetime):
    """A fixed datetime class for mocking datetime.now()."""
    @classmethod
    def now(cls):
        return cls(2024, 1, 1)

def test_calculate_week_number_before_first_sunday(monkeypatch):
    monkeypatch.setattr(dateUtils, "datetime", FixedDatetime)
    result = dateUtils.calculate_week_number("January 2")
    assert result == 1

def test_calculate_week_number_on_first_sunday(monkeypatch):
    monkeypatch.setattr(dateUtils, "datetime", FixedDatetime)
    result = dateUtils.calculate_week_number("January 7")
    assert result == 2

def test_calculate_week_number_after_first_sunday(monkeypatch):
    monkeypatch.setattr(dateUtils, "datetime", FixedDatetime)
    result = dateUtils.calculate_week_number("January 14")
    assert result == 3

def test_calculate_week_number_end_of_year(monkeypatch):
    monkeypatch.setattr(dateUtils, "datetime", FixedDatetime)
    result = dateUtils.calculate_week_number("December 29")
    current_year = 2024
    first_jan = datetime(current_year, 1, 1)
    first_sunday = first_jan + timedelta(days=(6 - first_jan.weekday()) % 7)
    full_date = datetime.strptime(f"{current_year} December 29", "%Y %B %d")
    weeks_passed = (full_date - first_sunday).days // 7
    expected = weeks_passed + 2
    assert result == expected

def test_calculate_week_number_on_first_jan(monkeypatch):
    monkeypatch.setattr(dateUtils, "datetime", FixedDatetime)
    result = dateUtils.calculate_week_number("January 1")
    assert result == 1

def test_calculate_week_number_on_last_day(monkeypatch):
    monkeypatch.setattr(dateUtils, "datetime", FixedDatetime)
    result = dateUtils.calculate_week_number("December 31")
    current_year = 2024
    first_jan = datetime(current_year, 1, 1)
    first_sunday = first_jan + timedelta(days=(6 - first_jan.weekday()) % 7)
    full_date = datetime.strptime(f"{current_year} December 31", "%Y %B %d")
    weeks_passed = (full_date - first_sunday).days // 7
    expected = weeks_passed + 2
    assert result == expected

def test_get_this_week_sunday_format(monkeypatch):
    monkeypatch.setattr(dateUtils, "datetime", FixedDatetime)
    result = dateUtils.get_this_week_sunday("January 7")
    assert result == "1/7/2024"

def test_get_this_week_sunday_leading_zeros(monkeypatch):
    monkeypatch.setattr(dateUtils, "datetime", FixedDatetime)
    result = dateUtils.get_this_week_sunday("March 3")
    assert result == "3/3/2024"

def test_get_this_week_sunday_end_of_year(monkeypatch):
    monkeypatch.setattr(dateUtils, "datetime", FixedDatetime)
    result = dateUtils.get_this_week_sunday("December 31")
    assert result == "12/31/2024"

def test_get_this_week_sunday_single_digit(monkeypatch):
    monkeypatch.setattr(dateUtils, "datetime", FixedDatetime)
    result = dateUtils.get_this_week_sunday("February 2")
    assert result == "2/2/2024"

def test_calculate_week_number_invalid_date(monkeypatch):
    monkeypatch.setattr(dateUtils, "datetime", FixedDatetime)
    with pytest.raises(ValueError):
        dateUtils.calculate_week_number("Foo 99")

def test_get_this_week_sunday_invalid_date(monkeypatch):
    monkeypatch.setattr(dateUtils, "datetime", FixedDatetime)
    with pytest.raises(ValueError):
        dateUtils.get_this_week_sunday("Bar 99")