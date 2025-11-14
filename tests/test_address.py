"""Tests for the Address class."""

import pytest
from src.models.address import Address


def test_address_initialization_with_all_fields():
    """Test that Address initializes with country, city, and address_line."""
    address = Address("UA", "Kyiv", "Main St 1")
    assert address.country == "UA"
    assert address.city == "Kyiv"
    assert address.address_line == "Main St 1"


def test_address_initialization_with_empty_strings():
    """Test that Address handles empty strings by converting to None."""
    address = Address("", "", "")
    assert address.country is None
    assert address.city is None
    assert address.address_line is None


def test_address_strips_whitespace():
    """Test that Address strips whitespace from fields."""
    address = Address("  UA  ", "  Kyiv  ", "  Main St 1  ")
    assert address.country == "UA"
    assert address.city == "Kyiv"
    assert address.address_line == "Main St 1"


def test_address_is_empty_with_all_none():
    """Test that is_empty returns True when all fields are None."""
    address = Address("", "", "")
    assert address.is_empty() is True


def test_address_is_empty_with_all_empty_strings():
    """Test that is_empty returns True when all fields are empty strings."""
    address = Address(None, None, None)
    assert address.is_empty() is True


def test_address_is_not_empty_with_country():
    """Test that is_empty returns False when country is set."""
    address = Address("UA", "", "")
    assert address.is_empty() is False


def test_address_is_not_empty_with_city():
    """Test that is_empty returns False when city is set."""
    address = Address("", "Kyiv", "")
    assert address.is_empty() is False


def test_address_is_not_empty_with_address_line():
    """Test that is_empty returns False when address_line is set."""
    address = Address("", "", "Main St 1")
    assert address.is_empty() is False


def test_address_str_representation_with_all_fields():
    """Test that __str__ returns formatted string with all fields."""
    address = Address("UA", "Kyiv", "Main St 1")
    assert str(address) == "Main St 1, Kyiv, UA"


def test_address_str_representation_with_country_only():
    """Test that __str__ returns only country when other fields are empty."""
    address = Address("UA", "", "")
    assert str(address) == "UA"


def test_address_str_representation_with_city_only():
    """Test that __str__ returns only city when other fields are empty."""
    address = Address("", "Kyiv", "")
    assert str(address) == "Kyiv"


def test_address_str_representation_with_address_line_only():
    """Test that __str__ returns only address_line when other fields are empty."""
    address = Address("", "", "Main St 1")
    assert str(address) == "Main St 1"


def test_address_str_representation_with_country_and_city():
    """Test that __str__ returns country and city when address_line is empty."""
    address = Address("UA", "Kyiv", "")
    assert str(address) == "Kyiv, UA"


def test_address_str_representation_with_city_and_address_line():
    """Test that __str__ returns city and address_line when country is empty."""
    address = Address("", "Kyiv", "Main St 1")
    assert str(address) == "Main St 1, Kyiv"


def test_address_str_representation_empty():
    """Test that __str__ returns empty string when address is empty."""
    address = Address("", "", "")
    assert str(address) == ""


def test_address_repr_representation():
    """Test that __repr__ returns correct representation."""
    address = Address("UA", "Kyiv", "Main St 1")
    assert repr(address) == "Address(country='UA', city='Kyiv', address_line='Main St 1')"


def test_address_equality():
    """Test that two Address objects with same values are equal."""
    address1 = Address("UA", "Kyiv", "Main St 1")
    address2 = Address("UA", "Kyiv", "Main St 1")
    assert address1 == address2


def test_address_equality_different_country():
    """Test that two Address objects with different countries are not equal."""
    address1 = Address("UA", "Kyiv", "Main St 1")
    address2 = Address("PL", "Kyiv", "Main St 1")
    assert address1 != address2


def test_address_equality_different_city():
    """Test that two Address objects with different cities are not equal."""
    address1 = Address("UA", "Kyiv", "Main St 1")
    address2 = Address("UA", "Lviv", "Main St 1")
    assert address1 != address2


def test_address_equality_different_address_line():
    """Test that two Address objects with different address_lines are not equal."""
    address1 = Address("UA", "Kyiv", "Main St 1")
    address2 = Address("UA", "Kyiv", "Main St 2")
    assert address1 != address2


def test_address_equality_with_none_values():
    """Test that two Address objects with None values are equal."""
    address1 = Address("", "", "")
    address2 = Address("", "", "")
    assert address1 == address2


def test_address_equality_with_non_address_object():
    """Test that Address comparison with non-Address object returns NotImplemented."""
    address = Address("UA", "Kyiv", "Main St 1")
    assert address.__eq__("not an address") == NotImplemented

