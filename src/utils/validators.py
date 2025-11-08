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

from datetime import datetime

import typer


def validate_phone(value: str) -> str:
    """
    Validate phone number format for CLI input.

    Phone numbers must be exactly 10 digits.

    Args:
        value: Phone number string

    Returns:
        Validated phone number

    Raises:
        typer.BadParameter: If phone format is invalid
    """
    if not value.isdigit():
        raise typer.BadParameter("Phone number must contain only digits")
    if len(value) != 10:
        raise typer.BadParameter("Phone number must be exactly 10 digits")
    return value


def validate_birthday(value: str) -> str:
    """
    Validate birthday date format for CLI input.

    Birthdays must be in DD.MM.YYYY format.

    Args:
        value: Birthday string in DD.MM.YYYY format

    Returns:
        Validated birthday string

    Raises:
        typer.BadParameter: If date format is invalid
    """
    try:
        datetime.strptime(value, "%d.%m.%Y")
        return value
    except ValueError:
        raise typer.BadParameter(
            "Invalid date format. Use DD.MM.YYYY (e.g., 25.12.1990)"
        )


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
    if "@" not in value or "." not in value:
        raise typer.BadParameter("Invalid email format")
    return value


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
