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

class TestPhoneValidator:
    def test_validate_phone_valid_local_10_digits(self):
        assert validate_phone("0123456789") == "0123456789"

    def test_validate_phone_normalizes_spaces_and_dashes(self):
        assert validate_phone("0 123-456-789") == "0123456789"
        assert validate_phone("(012) 345-67-89") == "0123456789"

    def test_validate_phone_ua_international_without_plus(self):
        assert validate_phone("380123456789") == "0123456789"

    def test_validate_phone_letters_rejected(self):
        with pytest.raises(typer.BadParameter) as exc:
            validate_phone("12345abcde")
        assert "letter" in str(exc.value).lower()

    def test_validate_phone_too_short_rejected(self):
        with pytest.raises(typer.BadParameter) as exc:
            validate_phone("123")
        assert "exactly 10" in str(exc.value).lower()

    def test_validate_phone_all_identical_digits_rejected(self):
        with pytest.raises(typer.BadParameter) as exc:
            validate_phone("0000000000")
        assert "identical" in str(exc.value).lower()

    def test_validate_phone_long_but_reducible_to_10(self):
        # US-Canada like 11 digits without '+', NSN=[1:] -> accept last 10 via libphonenumber path
        out = validate_phone("16502530000")
        assert len(out) == 10
        assert out.isdigit()

    def test_validate_phone_too_long_not_reducible(self):
        with pytest.raises(typer.BadParameter):
            validate_phone("9999999999999")

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