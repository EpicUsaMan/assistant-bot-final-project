"""Tests for the Phone class with libphonenumber-backed logic."""

import pytest
from phonenumbers import NumberParseException

from src.models.phone import Phone


def test_phone_accepts_local_ua_number():
    phone = Phone("067-235-5960")
    assert phone.value == "+380672355960"
    assert phone.display_value == "+380 67 235 5960"
    assert phone.country_code == 380
    assert phone.national_number == 672355960


def test_phone_rejects_non_ukrainian_number():
    """Test that non-Ukrainian phone numbers are rejected (system is UA-only)."""
    with pytest.raises(ValueError, match="Phone number must be exactly 10 digits"):
        Phone("+1 (650) 253-0000")  # US number with 10 digits, should be rejected


def test_phone_accepts_ukrainian_international_number_without_plus():
    phone = Phone("0038 067 235 5960")
    assert phone.value == "+380672355960"
    assert phone.display_value == "+380 67 235 5960"


def test_phone_invalid_number_raises_value_error():
    with pytest.raises(ValueError, match="Phone number is not possible: 123"):
        Phone("123")

    with pytest.raises(ValueError, match="Phone number cannot be empty"):
        Phone("  ")
    
    # Test that 11-digit numbers are rejected
    with pytest.raises(ValueError, match="Phone number must be exactly 10 digits.* got 11 digits"):
        Phone("09758367551")  # 11 digits instead of 10


def test_phone_display_value_national():
    phone = Phone("0672355960")
    assert phone.display_value_national in {"067 235 5960", "(067) 235 5960"}


def test_phone_equality_based_on_canonical():
    assert Phone("0672355960") == Phone("+380672355960")


def test_phone_str_returns_display_value():
    phone = Phone("0672355960")
    assert str(phone) == phone.display_value
