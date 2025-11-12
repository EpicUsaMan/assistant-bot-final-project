"""
Tests for parameter validators (CLI boundary).
Adjusted to match improved validators:
- phone: flexible input, 10-digit output, reject letters
- birthday: DD.MM.YYYY, real date, no future, age <= 120
- email: simplified regex, lowercase normalization
"""
import pytest
import typer
from src.utils.validators import (
    validate_phone,
    validate_birthday,
    validate_email,
)
from src.utils.validators import validate_phone, validate_birthday, validate_email
from src.utils.validators import split_tags_string


class TestPhoneValidator:
    def test_validate_phone_local_number(self):
        assert validate_phone("067-235-5960") == "+380672355960"

    def test_validate_phone_international(self):
        assert validate_phone("+1 (650) 253-0000") == "+16502530000"

    def test_validate_phone_blank_raises(self):
        with pytest.raises(typer.BadParameter, match="cannot be empty"):
            validate_phone("  ")

    def test_validate_phone_invalid_format(self):
        with pytest.raises(typer.BadParameter, match="Phone number is not possible: abc123"):
            validate_phone("abc123")

    def test_validate_phone_not_possible(self):
        with pytest.raises(typer.BadParameter, match="Phone number is not possible"):
            validate_phone("123")

    def test_validate_phone_duplicate_formatting(self):
        first = validate_phone("0672355960")
        second = validate_phone("+380 67 235 5960")
        assert first == second == "+380672355960"

class TestBirthdayValidator:
    def test_validate_birthday_valid(self):
        assert validate_birthday("15.05.1990") == "15.05.1990"

    def test_validate_birthday_edge_cases(self):
        assert validate_birthday("01.01.2000") == "01.01.2000"
        assert validate_birthday("31.12.1999") == "31.12.1999"
        # Leap year
        assert validate_birthday("29.02.2004") == "29.02.2004"

    def test_validate_birthday_invalid_format(self):
        for bad in ["invalid", "15/05/1990", "15-05-1990", "1990.05.15", "32.13.2020"]:
            with pytest.raises(typer.BadParameter) as exc:
                validate_birthday(bad)
            assert "dd.mm.yyyy" in str(exc.value).lower()

    def test_validate_birthday_future(self):
        with pytest.raises(typer.BadParameter) as exc:
            validate_birthday("01.01.3000")
        assert "future" in str(exc.value).lower()

    def test_validate_birthday_too_old(self):
        with pytest.raises(typer.BadParameter) as exc:
            validate_birthday("01.01.1800")
        # Message may include "120" or "year must be"
        assert any(s in str(exc.value).lower() for s in ["120", "year"])

class TestEmailValidator:
    def test_validate_email_valid_normalized_lowercase(self):
        assert validate_email("USER.Name+tag@Example.COM") == "user.name+tag@example.com"

    def test_validate_email_invalids(self):
        bad_emails = [
            "", "plainaddress", "user@", "@mail.com", "user@mail",
            "user mail@mail.com", "user@mail..com", "user@@mail.com",
            "user@mail.c", "user@mail.corporationtoolongtoolong"
        ]
        for bad in bad_emails:
            with pytest.raises(typer.BadParameter) as exc:
                validate_email(bad)
            msg = str(exc.value).lower()
            assert any(s in msg for s in ["invalid email", "must not", "empty"])
# Additional tests for tag splitting utility
class TestTagSplitting:
    """Tests for tag splitting utility."""

    def test_split_tags_string_basic(self):
        assert split_tags_string("ml, ai ,python") == ["ml", "ai", "python"]

    def test_split_tags_string_quoted_comma(self):
        assert split_tags_string('"ml,ai", data') == ["ml,ai", "data"]

    def test_split_tags_string_spaces_only(self):
        assert split_tags_string("   ") == []

    def test_split_tags_string_empty(self):
        assert split_tags_string("") == []

    def test_split_tags_string_quotes_and_spaces(self):
        assert split_tags_string('  "a,b" ,  c  ') == ["a,b", "c"]
