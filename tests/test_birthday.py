"""Tests for the Birthday class."""

import pytest
from datetime import datetime
from src.models.birthday import Birthday


def test_birthday_valid_format():
    """Test that Birthday accepts valid DD.MM.YYYY format."""
    birthday = Birthday("15.05.1990")
    assert birthday.value == "15.05.1990"
    assert isinstance(birthday.date, datetime)


def test_birthday_date_property():
    """Test that Birthday.date returns datetime object."""
    birthday = Birthday("01.01.2000")
    date_obj = birthday.date
    assert isinstance(date_obj, datetime)
    assert date_obj.day == 1
    assert date_obj.month == 1
    assert date_obj.year == 2000


def test_birthday_invalid_format_wrong_separator():
    """Test that Birthday raises ValueError for wrong separator."""
    with pytest.raises(ValueError) as exc_info:
        Birthday("15-05-1990")
    assert "Invalid date format. Use DD.MM.YYYY" in str(exc_info.value)


def test_birthday_invalid_format_wrong_order():
    """Test that Birthday raises ValueError for wrong date order."""
    with pytest.raises(ValueError) as exc_info:
        Birthday("1990.05.15")
    assert "Invalid date format. Use DD.MM.YYYY" in str(exc_info.value)


def test_birthday_invalid_date():
    """Test that Birthday raises ValueError for invalid date."""
    with pytest.raises(ValueError) as exc_info:
        Birthday("32.01.2000")
    assert "Invalid date format. Use DD.MM.YYYY" in str(exc_info.value)


def test_birthday_invalid_month():
    """Test that Birthday raises ValueError for invalid month."""
    with pytest.raises(ValueError) as exc_info:
        Birthday("15.13.2000")
    assert "Invalid date format. Use DD.MM.YYYY" in str(exc_info.value)


def test_birthday_february_29_leap_year():
    """Test that Birthday accepts February 29 in leap year."""
    birthday = Birthday("29.02.2000")
    assert birthday.value == "29.02.2000"


def test_birthday_february_29_non_leap_year():
    """Test that Birthday raises ValueError for Feb 29 in non-leap year."""
    with pytest.raises(ValueError) as exc_info:
        Birthday("29.02.2001")
    assert "Invalid date format. Use DD.MM.YYYY" in str(exc_info.value)


def test_birthday_str_representation():
    """Test that __str__ returns the original string format."""
    birthday = Birthday("15.05.1990")
    assert str(birthday) == "15.05.1990"


def test_birthday_empty_string():
    """Test that Birthday raises ValueError for empty string."""
    with pytest.raises(ValueError) as exc_info:
        Birthday("")
    assert "Invalid date format. Use DD.MM.YYYY" in str(exc_info.value)


def test_birthday_with_text():
    """Test that Birthday raises ValueError for text input."""
    with pytest.raises(ValueError) as exc_info:
        Birthday("January 15, 1990")
    assert "Invalid date format. Use DD.MM.YYYY" in str(exc_info.value)


def test_birthday_equality():
    """Test that two Birthday objects with same value are equal."""
    birthday1 = Birthday("15.05.1990")
    birthday2 = Birthday("15.05.1990")
    assert birthday1 == birthday2


def test_birthday_inequality():
    """Test that two Birthday objects with different values are not equal."""
    birthday1 = Birthday("15.05.1990")
    birthday2 = Birthday("16.05.1990")
    assert birthday1 != birthday2






