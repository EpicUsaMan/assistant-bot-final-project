"""Tests for the Field base class."""

import pytest
from src.models.field import Field


def test_field_initialization():
    """Test that Field initializes with a value."""
    field = Field("test value")
    assert field.value == "test value"


def test_field_str_representation():
    """Test that Field returns correct string representation."""
    field = Field("test")
    assert str(field) == "test"


def test_field_repr_representation():
    """Test that Field returns correct repr representation."""
    field = Field("test")
    assert repr(field) == "Field(value='test')"


def test_field_equality_with_same_value():
    """Test that two Field objects with same value are equal."""
    field1 = Field("test")
    field2 = Field("test")
    assert field1 == field2


def test_field_equality_with_different_value():
    """Test that two Field objects with different values are not equal."""
    field1 = Field("test1")
    field2 = Field("test2")
    assert field1 != field2


def test_field_equality_with_non_field_object():
    """Test that Field comparison with non-Field object returns NotImplemented."""
    field = Field("test")
    assert field.__eq__("test") == NotImplemented


def test_field_with_numeric_value():
    """Test that Field can store numeric values as strings."""
    field = Field(123)
    assert str(field) == "123"


def test_field_with_empty_string():
    """Test that Field can store empty string."""
    field = Field("")
    assert field.value == ""

