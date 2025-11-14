# src/models/phone.py
"""Phone field class with international parsing/formatting."""

from dataclasses import dataclass
from typing import ClassVar

import phonenumbers
from phonenumbers import PhoneNumberFormat

from src.models.field import Field

DEFAULT_REGION: str = "UA"  # default region is Ukraine

@dataclass(frozen=True)
class NormalizedPhone:
    canonical: str
    country_code: int
    national_number: int
    display_international: str
    display_national: str


class Phone(Field):
    """
    Wrapper around phonenumbers for consistent parsing, validation
    and formatting.

    Attributes:
        value: Canonical E.164 string (e.g. +380672355960)
    """

    _DEFAULT_REGION: ClassVar[str] = DEFAULT_REGION

    def __init__(self, raw: str) -> None:
        normalized = self._parse(raw)
        self._country_code = normalized.country_code
        self._national_number = normalized.national_number
        self._display_international = normalized.display_international
        self._display_national = normalized.display_national
        super().__init__(normalized.canonical)

    @property
    def country_code(self) -> int:
        return self._country_code

    @property
    def national_number(self) -> int:
        return self._national_number

    @property
    def display_value(self) -> str:
        """Default human-friendly representation."""
        return self._display_international

    @property
    def display_value_national(self) -> str:
        return self._display_national

    def __str__(self) -> str:
        return self.display_value

    def _parse(self, raw: str) -> NormalizedPhone:
        if raw is None:
            raise ValueError("Phone number cannot be empty")
        stripped = raw.strip()
        if not stripped:
            raise ValueError("Phone number cannot be empty")

        try:
            parsed = phonenumbers.parse(stripped, self._DEFAULT_REGION)
        except phonenumbers.NumberParseException as exc:
            raise ValueError(f"Invalid phone number: {stripped}") from exc

        if not phonenumbers.is_possible_number(parsed):
            raise ValueError(f"Phone number is not possible: {stripped}")

        canonical = phonenumbers.format_number(parsed, PhoneNumberFormat.E164)
        display_intl = phonenumbers.format_number(parsed, PhoneNumberFormat.INTERNATIONAL)
        display_nat = phonenumbers.format_number(parsed, PhoneNumberFormat.NATIONAL)

        return NormalizedPhone(
            canonical=canonical,
            country_code=parsed.country_code,
            national_number=parsed.national_number,
            display_international=display_intl,
            display_national=display_nat,
        )