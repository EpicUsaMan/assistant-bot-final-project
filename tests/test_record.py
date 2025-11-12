"""Tests for the Record class."""

import pytest
from src.models.record import Record
from src.models.name import Name
from src.models.tags import Tags


def test_record_initialization():
    """Test that Record initializes with a name."""
    record = Record("John")
    assert record.name.value == "John"
    assert record.phones == []
    assert record.birthday is None


def test_record_add_phone():
    """Test that Record can add a phone number."""
    record = Record("John")
    record.add_phone("0672355960")
    assert len(record.phones) == 1
    assert record.phones[0].value == "+380672355960"
    assert record.phones[0].display_value == "+380 67 235 5960"


def test_record_add_multiple_phones():
    """Test that Record can add multiple phone numbers."""
    record = Record("John")
    record.add_phone("0123456789")
    record.add_phone("0987654321")
    assert len(record.phones) == 2


def test_record_add_duplicate_phone_raises_error():
    """Test that adding duplicate phone raises ValueError."""
    record = Record("John")
    record.add_phone("0123456789")
    with pytest.raises(ValueError, match="Phone 0123456789 already exists"):
        record.add_phone("0123456789")


def test_record_add_invalid_phone_raises_error():
    """Test that adding invalid phone raises ValueError."""
    record = Record("John")
    with pytest.raises(ValueError, match="Phone number is not possible: 123"):
        record.add_phone("123")


def test_record_remove_phone():
    """Test that Record can remove a phone number."""
    record = Record("John")
    record.add_phone("0123456789")
    record.remove_phone("0123456789")
    assert len(record.phones) == 0


def test_record_remove_non_existent_phone_raises_error():
    """Test that removing non-existent phone raises ValueError."""
    record = Record("John")
    with pytest.raises(ValueError, match="Phone 0123456789 not found"):
        record.remove_phone("0123456789")


def test_record_edit_phone():
    """Test that Record can edit a phone number."""
    record = Record("John")
    record.add_phone("0123456789")
    record.edit_phone("0123456789", "0987654321")
    assert record.phones[0].value == "+380987654321"
    assert record.phones[0].display_value == "+380 98 765 4321"

def test_record_edit_non_existent_phone_raises_error():
    """Test that editing non-existent phone raises ValueError."""
    record = Record("John")
    with pytest.raises(ValueError, match="Phone 0123456789 not found"):
        record.edit_phone("0123456789", "0987654321")


def test_record_edit_to_invalid_phone_raises_error():
    """Test that editing to invalid phone raises ValueError."""
    record = Record("John")
    record.add_phone("0123456789")
    with pytest.raises(ValueError, match=f"Phone number is not possible: 123"):
        record.edit_phone("0123456789", "123")

def test_record_find_phone():
    """Test that Record can find a phone number."""
    record = Record("John")
    record.add_phone("0123456789")
    record.add_phone("0987654321")
    found_phone = record.find_phone("0987654321")
    assert found_phone is not None
    assert found_phone.value == "+380987654321"
    assert found_phone.display_value == "+380 98 765 4321"

def test_record_find_non_existent_phone():
    """Test that finding non-existent phone returns None."""
    record = Record("John")
    record.add_phone("0123456789")
    found_phone = record.find_phone("0987654321")
    assert found_phone is None


def test_record_str_representation():
    """Test that Record returns correct string representation."""
    record = Record("John")
    record.add_phone("0123456789")
    record.add_phone("0987654321")
    assert str(record) == "Contact name: John, phones: +380 123456789; +380 98 765 4321"


def test_record_str_representation_without_phones():
    """Test that Record string representation works without phones."""
    record = Record("John")
    assert str(record) == "Contact name: John, phones: "


def test_record_repr_representation():
    """Test that Record returns correct repr representation."""
    record = Record("John")
    record.add_phone("0123456789")
    assert repr(record) == "Record(name='John', phones=['+380123456789'])"


def test_record_add_birthday():
    """Test that Record can add a birthday."""
    record = Record("John")
    record.add_birthday("15.05.1990")
    assert record.birthday is not None
    assert record.birthday.value == "15.05.1990"


def test_record_add_invalid_birthday_raises_error():
    """Test that adding invalid birthday raises ValueError."""
    record = Record("John")
    with pytest.raises(ValueError, match="Invalid date format. Use DD.MM.YYYY"):
        record.add_birthday("1990-05-15")


def test_record_str_representation_with_birthday():
    """Test that Record string representation includes birthday."""
    record = Record("John")
    record.add_phone("0123456789")
    record.add_birthday("15.05.1990")
    assert str(record) == "Contact name: John, phones: +380 123456789, birthday: 15.05.1990"


def test_record_str_representation_with_birthday_no_phones():
    """Test that Record string representation with birthday but no phones."""
    record = Record("John")
    record.add_birthday("15.05.1990")
    assert str(record) == "Contact name: John, phones: , birthday: 15.05.1990"


def test_record_update_birthday():
    """Test that Record can update an existing birthday."""
    record = Record("John")
    record.add_birthday("15.05.1990")
    record.add_birthday("16.05.1991")
    assert record.birthday.value == "16.05.1991"

def test_record_setstate_migrates_legacy_phones():
    state = {
        "name": Name("John"),
        "phones": ["0123456789", "0672355960"],
        "birthday": None,
        "tags": Tags(),
    }
    record = Record("dummy")  # will be overwritten
    record.__setstate__(state)
    assert record.phones[0].value == "+380123456789"
    assert record.phones[1].display_value == "+380 67 235 5960"

def test_record_remove_phone_accepts_flexible_input():
    record = Record("John")
    record.add_phone("+380672355960")
    record.remove_phone("067-235-59-60")
    assert not record.phones

def test_record_add_duplicate_phone_detects_formatted_numbers():
    """Adding the same phone in another format should still raise ValueError."""
    record = Record("John")
    record.add_phone("067-235-59-60")
    with pytest.raises(ValueError, match=r"Phone \+380 67 235 5960 already exists for this contact"):
        record.add_phone("+380 67 235 5960")


def test_record_find_phone_accepts_formatted_input():
    """find_phone should understand formatted strings."""
    record = Record("John")
    record.add_phone("0987654321")
    found = record.find_phone("(098) 765-4321")
    assert found is not None
    assert found.value == "+380987654321"


def test_record_edit_phone_accepts_formatted_old_number():
    """edit_phone should normalize the old phone argument."""
    record = Record("John")
    record.add_phone("0987654321")
    record.edit_phone("(098) 765-4321", "0501234567")
    assert record.phones[0].value == "+380501234567"
    assert record.phones[0].display_value.startswith("+380")


def test_record_str_with_birthday_uses_formatted_phone():
    """String representation with birthday should use formatted phones."""
    record = Record("John")
    record.add_phone("0501234567")
    record.add_birthday("15.05.1990")
    assert "+380" in str(record)  # international format present
    assert "birthday: 15.05.1990" in str(record)