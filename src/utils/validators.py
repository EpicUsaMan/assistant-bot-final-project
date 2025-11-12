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
from datetime import datetime, date
from src.models.phone import Phone

_ACEPTED_PHONE_LEN = 10
_MAX_AGE_YEARS = 120
_BDAY_FMT = "%d.%m.%Y"
_EMAIL_RE = re.compile(r"^(?P<local>[A-Za-z0-9._%+-]+)@(?P<domain>[A-Za-z0-9.-]+\.[A-Za-z]{2,24})$")

def validate_phone(value: str) -> str:
    """Normalize phone number (flexible input → E.164 string)."""
    raw = (value or "").strip()
    if not raw:
        raise typer.BadParameter("Phone number cannot be empty")

    try:
        phone = Phone(raw)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    return phone.value


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


# Tag validation utilities

import re
# splitting strings with commas safely
import csv
from io import StringIO

# Regular expression for valid tags: lowercase letters, digits, underscores, hyphens, 1-32 chars
_TAG_RE = re.compile(r"^[a-z0-9_,\-]{1,32}$")


def normalize_tag(tag: str) -> str:
    """
    Normalize a tag by trimming whitespace, collapsing spaces, and converting to lowercase.
    """
    # trim → collapse spaces → lowercase
    return " ".join(tag.strip().split()).lower()


def is_valid_tag(tag: str) -> bool:
    """
    Check if a tag is valid according to the defined pattern.
    """
    # empty tags already handled in normalize_tag
    return bool(tag) and bool(_TAG_RE.match(tag))


def split_tags_string(s: str) -> list[str]:
    """
    Split a comma-separated string into a list of tags.
    Args:
        s: Comma-separated tags string
    Returns:
        List of tag strings
    
    Tags with commas are supported if quoted.
    """
    # "ai, ML" ,  python -> ["ai, ML", "python"] (without normalization)
    if not s or not s.strip():
        return []
    reader = csv.reader(StringIO(s), skipinitialspace=True)
    row = next(reader, [])
    return [t.strip() for t in row if t and t.strip()]


def validate_tag(value: str) -> str:
    """
    Validate a single tag for CLI input.
    Args:
        value: Tag string
    Returns:
        Validated tag string
    """
    n = normalize_tag(value)
    if not is_valid_tag(n):
        raise typer.BadParameter("Tag must match [a-z0-9_,-] and be 1..32 chars")
    return n
