"""Tests for the Name class."""

import pytest
from src.models.name import Name


def test_name_initialization_with_valid_name():
    """Test that Name initializes with a valid name."""
    name = Name("John Doe")
    assert name.value == "John Doe"


def test_name_strips_whitespace():
    """Test that Name strips leading and trailing whitespace."""
    name = Name("  John Doe  ")
    assert name.value == "John Doe"


def test_name_with_empty_string_raises_error():
    """Test that Name raises ValueError for empty string."""
    with pytest.raises(ValueError, match="Name cannot be empty"):
        Name("")


def test_name_with_only_whitespace_raises_error():
    """Test that Name raises ValueError for whitespace-only string."""
    with pytest.raises(ValueError, match="Name cannot be empty"):
        Name("   ")


def test_name_inheritance_from_field():
    """Test that Name inherits from Field and has str method."""
    name = Name("Alice")
    assert str(name) == "Alice"


def test_name_with_single_character():
    """Test that Name accepts single character names."""
    name = Name("A")
    assert name.value == "A"


def test_name_with_special_characters():
    """Test that Name accepts names with special characters."""
    name = Name("O'Brien-Smith")
    assert name.value == "O'Brien-Smith"


def test_name_equality():
    """Test that two Name objects with same value are equal."""
    name1 = Name("John")
    name2 = Name("John")
    assert name1 == name2

