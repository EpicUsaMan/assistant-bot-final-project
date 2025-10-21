"""
Tests for parameter validators.

This module tests the Typer callback validators to ensure they properly
validate input parameters at the CLI boundary.
"""

import pytest
import typer
from src.utils.validators import validate_phone, validate_birthday, validate_email


class TestPhoneValidator:
    """Tests for phone number validator."""
    
    def test_validate_phone_valid(self):
        """Test validation passes for valid 10-digit phone."""
        result = validate_phone("1234567890")
        assert result == "1234567890"
    
    def test_validate_phone_not_digits(self):
        """Test validation fails for non-digit characters."""
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_phone("12345abcde")
        assert "must contain only digits" in str(exc_info.value)
    
    def test_validate_phone_letters(self):
        """Test validation fails for letters."""
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_phone("invalid")
        assert "must contain only digits" in str(exc_info.value)
    
    def test_validate_phone_too_short(self):
        """Test validation fails for phone shorter than 10 digits."""
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_phone("123")
        assert "must be exactly 10 digits" in str(exc_info.value)
    
    def test_validate_phone_too_long(self):
        """Test validation fails for phone longer than 10 digits."""
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_phone("12345678901")
        assert "must be exactly 10 digits" in str(exc_info.value)
    
    def test_validate_phone_with_spaces(self):
        """Test validation fails for phone with spaces."""
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_phone("123 456 7890")
        assert "must contain only digits" in str(exc_info.value)
    
    def test_validate_phone_with_dashes(self):
        """Test validation fails for phone with dashes."""
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_phone("123-456-7890")
        assert "must contain only digits" in str(exc_info.value)


class TestBirthdayValidator:
    """Tests for birthday date validator."""
    
    def test_validate_birthday_valid(self):
        """Test validation passes for valid DD.MM.YYYY date."""
        result = validate_birthday("15.05.1990")
        assert result == "15.05.1990"
    
    def test_validate_birthday_valid_edge_cases(self):
        """Test validation passes for edge case dates."""
        assert validate_birthday("01.01.2000") == "01.01.2000"
        assert validate_birthday("31.12.1999") == "31.12.1999"
        assert validate_birthday("29.02.2020") == "29.02.2020"
    
    def test_validate_birthday_invalid_format(self):
        """Test validation fails for invalid format."""
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_birthday("invalid")
        assert "Invalid date format" in str(exc_info.value)
        assert "DD.MM.YYYY" in str(exc_info.value)
    
    def test_validate_birthday_wrong_format_slash(self):
        """Test validation fails for wrong separator."""
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_birthday("15/05/1990")
        assert "Invalid date format" in str(exc_info.value)
    
    def test_validate_birthday_wrong_format_dash(self):
        """Test validation fails for wrong separator."""
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_birthday("15-05-1990")
        assert "Invalid date format" in str(exc_info.value)
    
    def test_validate_birthday_wrong_order_yyyy_mm_dd(self):
        """Test validation fails for YYYY-MM-DD format."""
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_birthday("1990.05.15")
        assert "Invalid date format" in str(exc_info.value)
    
    def test_validate_birthday_invalid_date(self):
        """Test validation fails for invalid date values."""
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_birthday("32.13.2020")
        assert "Invalid date format" in str(exc_info.value)
    
    def test_validate_birthday_invalid_day(self):
        """Test validation fails for invalid day."""
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_birthday("00.05.1990")
        assert "Invalid date format" in str(exc_info.value)
    
    def test_validate_birthday_invalid_month(self):
        """Test validation fails for invalid month."""
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_birthday("15.13.1990")
        assert "Invalid date format" in str(exc_info.value)
    
    def test_validate_birthday_february_30(self):
        """Test validation fails for February 30th."""
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_birthday("30.02.2020")
        assert "Invalid date format" in str(exc_info.value)


class TestEmailValidator:
    """Tests for email validator."""
    
    def test_validate_email_valid(self):
        """Test validation passes for valid email."""
        result = validate_email("test@example.com")
        assert result == "test@example.com"
    
    def test_validate_email_no_at_sign(self):
        """Test validation fails for email without @ sign."""
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_email("testexample.com")
        assert "Invalid email format" in str(exc_info.value)
    
    def test_validate_email_no_dot(self):
        """Test validation fails for email without dot."""
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_email("test@example")
        assert "Invalid email format" in str(exc_info.value)
    
    def test_validate_email_invalid(self):
        """Test validation fails for completely invalid email."""
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_email("invalid")
        assert "Invalid email format" in str(exc_info.value)

