"""Tests for the Email class."""

import pytest
from src.models.email import Email


def test_email_initialization_with_valid_address():
    """Test that Email initializes with a valid email address."""
    email = Email("user@example.com")
    assert email.value == "user@example.com"


def test_email_normalizes_to_lowercase():
    """Test that Email normalizes email to lowercase."""
    email = Email("USER.Name+tag@Example.COM")
    assert email.value == "user.name+tag@example.com"


def test_email_with_invalid_format_raises_error():
    """Test that Email raises ValueError for invalid email format."""
    with pytest.raises(ValueError):
        Email("invalid-email")


def test_email_with_empty_string_raises_error():
    """Test that Email raises ValueError for empty string."""
    with pytest.raises(ValueError):
        Email("")


def test_email_with_missing_at_symbol_raises_error():
    """Test that Email raises ValueError for email without @."""
    with pytest.raises(ValueError):
        Email("userexample.com")


def test_email_with_missing_domain_raises_error():
    """Test that Email raises ValueError for email without domain."""
    with pytest.raises(ValueError):
        Email("user@")


def test_email_with_missing_local_part_raises_error():
    """Test that Email raises ValueError for email without local part."""
    with pytest.raises(ValueError):
        Email("@example.com")


def test_email_inheritance_from_field():
    """Test that Email inherits from Field and has str method."""
    email = Email("test@example.com")
    assert str(email) == "test@example.com"


def test_email_equality():
    """Test that two Email objects with same value are equal."""
    email1 = Email("user@example.com")
    email2 = Email("USER@EXAMPLE.COM")  # Should normalize to same value
    assert email1 == email2


def test_email_equality_different_values():
    """Test that two Email objects with different values are not equal."""
    email1 = Email("user1@example.com")
    email2 = Email("user2@example.com")
    assert email1 != email2


def test_email_with_plus_tag():
    """Test that Email accepts plus tags in local part."""
    email = Email("user+tag@example.com")
    assert email.value == "user+tag@example.com"


def test_email_with_dots_in_local_part():
    """Test that Email accepts dots in local part."""
    email = Email("user.name@example.com")
    assert email.value == "user.name@example.com"


def test_email_with_subdomain():
    """Test that Email accepts subdomains."""
    email = Email("user@mail.example.com")
    assert email.value == "user@mail.example.com"

