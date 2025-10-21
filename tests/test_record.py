"""Tests for the Record class."""

import pytest
from src.models.record import Record


def test_record_initialization():
    """Test that Record initializes with a name."""
    record = Record("John")
    assert record.name.value == "John"
    assert record.phones == []
    assert record.birthday is None


def test_record_add_phone():
    """Test that Record can add a phone number."""
    record = Record("John")
    record.add_phone("1234567890")
    assert len(record.phones) == 1
    assert record.phones[0].value == "1234567890"


def test_record_add_multiple_phones():
    """Test that Record can add multiple phone numbers."""
    record = Record("John")
    record.add_phone("1234567890")
    record.add_phone("0987654321")
    assert len(record.phones) == 2


def test_record_add_duplicate_phone_raises_error():
    """Test that adding duplicate phone raises ValueError."""
    record = Record("John")
    record.add_phone("1234567890")
    with pytest.raises(ValueError, match="Phone 1234567890 already exists"):
        record.add_phone("1234567890")


def test_record_add_invalid_phone_raises_error():
    """Test that adding invalid phone raises ValueError."""
    record = Record("John")
    with pytest.raises(ValueError, match="Phone number must be exactly 10 digits"):
        record.add_phone("123")


def test_record_remove_phone():
    """Test that Record can remove a phone number."""
    record = Record("John")
    record.add_phone("1234567890")
    record.remove_phone("1234567890")
    assert len(record.phones) == 0


def test_record_remove_non_existent_phone_raises_error():
    """Test that removing non-existent phone raises ValueError."""
    record = Record("John")
    with pytest.raises(ValueError, match="Phone 1234567890 not found"):
        record.remove_phone("1234567890")


def test_record_edit_phone():
    """Test that Record can edit a phone number."""
    record = Record("John")
    record.add_phone("1234567890")
    record.edit_phone("1234567890", "0987654321")
    assert record.phones[0].value == "0987654321"


def test_record_edit_non_existent_phone_raises_error():
    """Test that editing non-existent phone raises ValueError."""
    record = Record("John")
    with pytest.raises(ValueError, match="Phone 1234567890 not found"):
        record.edit_phone("1234567890", "0987654321")


def test_record_edit_to_invalid_phone_raises_error():
    """Test that editing to invalid phone raises ValueError."""
    record = Record("John")
    record.add_phone("1234567890")
    with pytest.raises(ValueError, match="Phone number must be exactly 10 digits"):
        record.edit_phone("1234567890", "123")


def test_record_find_phone():
    """Test that Record can find a phone number."""
    record = Record("John")
    record.add_phone("1234567890")
    record.add_phone("0987654321")
    found_phone = record.find_phone("0987654321")
    assert found_phone is not None
    assert found_phone.value == "0987654321"


def test_record_find_non_existent_phone():
    """Test that finding non-existent phone returns None."""
    record = Record("John")
    record.add_phone("1234567890")
    found_phone = record.find_phone("0987654321")
    assert found_phone is None


def test_record_str_representation():
    """Test that Record returns correct string representation."""
    record = Record("John")
    record.add_phone("1234567890")
    record.add_phone("0987654321")
    assert str(record) == "Contact name: John, phones: 1234567890; 0987654321"


def test_record_str_representation_without_phones():
    """Test that Record string representation works without phones."""
    record = Record("John")
    assert str(record) == "Contact name: John, phones: "


def test_record_repr_representation():
    """Test that Record returns correct repr representation."""
    record = Record("John")
    record.add_phone("1234567890")
    assert repr(record) == "Record(name='John', phones=['1234567890'])"


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
    record.add_phone("1234567890")
    record.add_birthday("15.05.1990")
    assert str(record) == "Contact name: John, phones: 1234567890, birthday: 15.05.1990"


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

