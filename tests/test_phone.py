"""Tests for the Phone class."""

import pytest
from src.models.phone import Phone


def test_phone_initialization_with_valid_number():
    """Test that Phone initializes with a valid 10-digit number."""
    phone = Phone("1234567890")
    assert phone.value == "1234567890"


def test_phone_with_non_digit_characters_raises_error():
    """Test that Phone raises ValueError for non-digit characters."""
    with pytest.raises(ValueError, match="Phone number must contain only digits"):
        Phone("123-456-7890")


def test_phone_with_letters_raises_error():
    """Test that Phone raises ValueError for letters in number."""
    with pytest.raises(ValueError, match="Phone number must contain only digits"):
        Phone("12345abcde")


def test_phone_with_less_than_10_digits_raises_error():
    """Test that Phone raises ValueError for less than 10 digits."""
    with pytest.raises(ValueError, match="Phone number must be exactly 10 digits"):
        Phone("123456789")


def test_phone_with_more_than_10_digits_raises_error():
    """Test that Phone raises ValueError for more than 10 digits."""
    with pytest.raises(ValueError, match="Phone number must be exactly 10 digits"):
        Phone("12345678901")


def test_phone_with_spaces_raises_error():
    """Test that Phone raises ValueError for spaces in number."""
    with pytest.raises(ValueError, match="Phone number must contain only digits"):
        Phone("123 456 7890")


def test_phone_inheritance_from_field():
    """Test that Phone inherits from Field and has str method."""
    phone = Phone("5555555555")
    assert str(phone) == "5555555555"


def test_phone_equality():
    """Test that two Phone objects with same number are equal."""
    phone1 = Phone("1234567890")
    phone2 = Phone("1234567890")
    assert phone1 == phone2


def test_phone_with_empty_string_raises_error():
    """Test that Phone raises ValueError for empty string."""
    with pytest.raises(ValueError, match="Phone number must contain only digits"):
        Phone("")

