"""
Parameter validators for CLI commands.

Each validator function is used as a Typer callback to validate
command arguments at the parameter level. This provides better UX
by showing users exactly which parameter has an invalid value.

When adding new fields with validation:
1. Create a validator function here following the template
2. Use it as callback in the command parameter definition
3. Typer will automatically show which parameter failed

Example:
    @app.command()
    def add_command(
        phone: str = typer.Argument(..., callback=validate_phone),
    ):
        ...
"""

import re
import typer
import phonenumbers
from datetime import datetime, date
from phonenumbers.phonenumberutil import NumberParseException, PhoneNumberType

_ACEPTED_PHONE_LEN = 10
_MIN_YEAR = 1900
_MAX_AGE_YEARS = 120
_BDAY_FMT = "%d.%m.%Y"
_EMAIL_RE = re.compile(r"^(?P<local>[A-Za-z0-9._%+-]+)@(?P<domain>[A-Za-z0-9.-]+\.[A-Za-z]{2,24})$")

def validate_phone(value: str) -> str:
    """
    Accept flexible input, validate by libphonenumber,
    and store EXACTLY 10 digits.

    Rules:
      - Letters are not allowed (explicit error).
      - If digits == 12 and start with '380' -> treat as UA and return '0' + last 9.
      - If digits == 10 -> accept as-is (after basic checks).

    Returns:
        10-digit string

    Raises:
        typer.BadParameter
    """

    raw = (value or "").strip()
    if not raw:
        raise typer.BadParameter("Phone is empty")

    # Only digits aceptable
    if re.search(r"[A-Za-z]", raw):
        raise typer.BadParameter("Phone must not contain letters")
    
    # Keep only digits for logic from here on
    digits = re.sub(r"\D+", "", raw)
    if not digits:
        raise typer.BadParameter("Phone must contain digits")

    # Fast-path UA in international: 380XXXXXXXXX -> 0XXXXXXXXX
    if len(digits) == 12 and digits.startswith("380"):
        normalized = "0" + digits[-9:]
        if re.fullmatch(r"^(\d)\1{9}$", normalized):
            raise typer.BadParameter("Phone looks invalid (all digits identical)")
        return normalized

    # Local 10-digit input
    if len(digits) == _ACEPTED_PHONE_LEN:
        # trivial input guard
        if re.fullmatch(r"^(\d)\1{9}$", digits):
            raise typer.BadParameter("Phone looks invalid (all digits identical)")
        return digits

    # For longer numbers, try to parse internationally
    if len(digits) > _ACEPTED_PHONE_LEN:
        try:
            num = phonenumbers.parse("+" + digits, None)
        except NumberParseException:
            raise typer.BadParameter(
                "Unsupported phone format. We store exactly 10 digits."
            )

        # Allow only person-reachable types
        typ = phonenumbers.number_type(num)
        if typ not in (
            PhoneNumberType.MOBILE,
            PhoneNumberType.FIXED_LINE,
            PhoneNumberType.FIXED_LINE_OR_MOBILE,
        ):
            raise typer.BadParameter("Unsupported phone type")

        nsn = phonenumbers.national_significant_number(num)
        region = phonenumbers.region_code_for_number(num)

        if len(nsn) == _ACEPTED_PHONE_LEN:
            normalized = nsn
        elif region == "UA" and len(nsn) == 9:
            normalized = "0" + nsn
        else:
            raise typer.BadParameter(
                f"We store exactly 10 digits. Your number's national part has "
                f"{len(nsn)} digits (region {region or 'unknown'})."
            )

        if re.fullmatch(r"^(\d)\1{9}$", normalized):
            raise typer.BadParameter("Phone looks invalid (all digits identical)")
        return normalized

    # Anything shorter than 10 digits is invalid
    raise typer.BadParameter("Phone must be exactly 10 digits")


def validate_birthday(value: str) -> str:
    """
    Validate a birthday in DD.MM.YYYY format.

    Extra checks:
      - must be a real date
      - cannot be in the future
      - age must be <= 120 years

    Returns normalized DD.MM.YYYY

    Raises typer.BadParameter on error.
    """
    raw = (value or "").strip()

    try:
        bday = datetime.strptime(raw, _BDAY_FMT).date()
    except ValueError:
        raise typer.BadParameter(
            "Invalid date. Use DD.MM.YYYY (e.g., 25.12.1990)"
        )

    today = date.today()

    # No future birthdays
    if bday > today:
        raise typer.BadParameter("Birthday cannot be in the future")

    # Age check (max 120)
    age = today.year - bday.year
    if age > _MAX_AGE_YEARS:
        raise typer.BadParameter(
            f"Birthday implies age {age}, which is not allowed (max {_MAX_AGE_YEARS})"
        )

    return bday.strftime(_BDAY_FMT)  # normalize formatting


def validate_email(value: str) -> str:
    """
    Validate email format for CLI input.
    
    Example validator for future use with email validation library.
    
    Args:
        value: Email string
        
    Returns:
        Validated email string
        
    Raises:
        typer.BadParameter: If email format is invalid
    """
    raw = (value or "").strip().lower()

    if not raw:
        raise typer.BadParameter("Email is empty")

    if " " in raw:
        raise typer.BadParameter("Email must not contain spaces")

    m = _EMAIL_RE.fullmatch(raw)
    if not m:
        raise typer.BadParameter("Invalid email format")

    local, domain = m.group("local"), m.group("domain")

    # reject local or domain starting/ending with dot or hyphen
    if local[0] in ".-" or local[-1] in ".-":
        raise typer.BadParameter("Invalid email: bad local part")
    if domain[0] in ".-" or domain[-1] in ".-":
        raise typer.BadParameter("Invalid email: bad domain")

    # reject consecutive dots
    if ".." in raw:
        raise typer.BadParameter("Invalid email: double dots are not allowed")

    return raw

