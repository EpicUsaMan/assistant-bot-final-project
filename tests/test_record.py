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
    assert str(record) == "Contact name: John"


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
    assert str(record) == "Contact name: John, birthday: 15.05.1990"


def test_record_update_birthday():
    """Test that Record can update an existing birthday."""
    record = Record("John")
    record.add_birthday("15.05.1990")
    record.add_birthday("16.05.1991")
    assert record.birthday.value == "16.05.1991"


# --- Note Management Tests ---

def test_record_initialization_includes_notes():
    """Test that Record initializes with empty notes dictionary."""
    record = Record("John")
    assert hasattr(record, "notes")
    assert record.notes == {}


def test_record_add_note():
    """Test that Record can add a note."""
    record = Record("John")
    record.add_note("Meeting", "Discuss project timeline")
    assert "Meeting" in record.notes
    assert record.notes["Meeting"].content == "Discuss project timeline"


def test_record_add_note_without_content():
    """Test that Record can add a note without content."""
    record = Record("John")
    record.add_note("Todo")
    assert "Todo" in record.notes
    assert record.notes["Todo"].content == ""


def test_record_add_duplicate_note_raises_error():
    """Test that adding duplicate note raises ValueError."""
    record = Record("John")
    record.add_note("Meeting", "Content 1")
    with pytest.raises(ValueError, match="Note 'Meeting' already exists"):
        record.add_note("Meeting", "Content 2")


def test_record_add_note_with_empty_name_raises_error():
    """Test that adding note with empty name raises ValueError."""
    record = Record("John")
    with pytest.raises(ValueError, match="Note name cannot be empty"):
        record.add_note("", "Some content")


def test_record_find_note():
    """Test that Record can find a note."""
    record = Record("John")
    record.add_note("Meeting", "Content")
    found_note = record.find_note("Meeting")
    assert found_note is not None
    assert found_note.name == "Meeting"


def test_record_find_non_existent_note():
    """Test that finding non-existent note returns None."""
    record = Record("John")
    record.add_note("Meeting", "Content")
    found_note = record.find_note("NonExistent")
    assert found_note is None


def test_record_edit_note():
    """Test that Record can edit a note's content."""
    record = Record("John")
    record.add_note("Meeting", "Original content")
    record.edit_note("Meeting", "Updated content")
    assert record.notes["Meeting"].content == "Updated content"


def test_record_edit_non_existent_note_raises_error():
    """Test that editing non-existent note raises ValueError."""
    record = Record("John")
    with pytest.raises(ValueError, match="Note 'NonExistent' not found"):
        record.edit_note("NonExistent", "New content")


def test_record_delete_note():
    """Test that Record can delete a note."""
    record = Record("John")
    record.add_note("Meeting", "Content")
    record.delete_note("Meeting")
    assert "Meeting" not in record.notes


def test_record_delete_non_existent_note_raises_error():
    """Test that deleting non-existent note raises ValueError."""
    record = Record("John")
    with pytest.raises(ValueError, match="Note 'NonExistent' not found"):
        record.delete_note("NonExistent")


def test_record_list_notes():
    """Test that Record can list all notes."""
    record = Record("John")
    record.add_note("Meeting", "Content 1")
    record.add_note("Todo", "Content 2")
    notes = record.list_notes()
    assert len(notes) == 2
    note_names = [note.name for note in notes]
    assert "Meeting" in note_names
    assert "Todo" in note_names


def test_record_list_notes_empty():
    """Test that list_notes returns empty list when no notes."""
    record = Record("John")
    notes = record.list_notes()
    assert notes == []


# --- Note Tag Management Tests ---

def test_record_note_add_tag():
    """Test that Record can add a tag to a note."""
    record = Record("John")
    record.add_note("Meeting", "Content")
    record.note_add_tag("Meeting", "important")
    assert "important" in record.notes["Meeting"].tags_list()


def test_record_note_add_tag_to_non_existent_note_raises_error():
    """Test that adding tag to non-existent note raises ValueError."""
    record = Record("John")
    with pytest.raises(ValueError, match="Note 'NonExistent' not found"):
        record.note_add_tag("NonExistent", "important")


def test_record_note_add_invalid_tag_raises_error():
    """Test that adding invalid tag to note raises ValueError."""
    record = Record("John")
    record.add_note("Meeting", "Content")
    with pytest.raises(ValueError, match="Invalid tag"):
        record.note_add_tag("Meeting", "")


def test_record_note_remove_tag():
    """Test that Record can remove a tag from a note."""
    record = Record("John")
    record.add_note("Meeting", "Content")
    record.note_add_tag("Meeting", "important")
    record.note_add_tag("Meeting", "urgent")
    record.note_remove_tag("Meeting", "important")
    assert "important" not in record.notes["Meeting"].tags_list()
    assert "urgent" in record.notes["Meeting"].tags_list()


def test_record_note_remove_tag_from_non_existent_note_raises_error():
    """Test that removing tag from non-existent note raises ValueError."""
    record = Record("John")
    with pytest.raises(ValueError, match="Note 'NonExistent' not found"):
        record.note_remove_tag("NonExistent", "important")


def test_record_note_clear_tags():
    """Test that Record can clear all tags from a note."""
    record = Record("John")
    record.add_note("Meeting", "Content")
    record.note_add_tag("Meeting", "important")
    record.note_add_tag("Meeting", "urgent")
    record.note_clear_tags("Meeting")
    assert record.notes["Meeting"].tags_list() == []


def test_record_note_clear_tags_from_non_existent_note_raises_error():
    """Test that clearing tags from non-existent note raises ValueError."""
    record = Record("John")
    with pytest.raises(ValueError, match="Note 'NonExistent' not found"):
        record.note_clear_tags("NonExistent")


def test_record_note_list_tags():
    """Test that Record can list all tags for a note."""
    record = Record("John")
    record.add_note("Meeting", "Content")
    record.note_add_tag("Meeting", "important")
    record.note_add_tag("Meeting", "work")
    tags = record.note_list_tags("Meeting")
    assert len(tags) == 2
    assert "important" in tags
    assert "work" in tags


def test_record_note_list_tags_from_non_existent_note_raises_error():
    """Test that listing tags from non-existent note raises ValueError."""
    record = Record("John")
    with pytest.raises(ValueError, match="Note 'NonExistent' not found"):
        record.note_list_tags("NonExistent")


# --- Email Management Tests ---

def test_record_initialization_includes_email():
    """Test that Record initializes with None email."""
    record = Record("John")
    assert record.email is None


def test_record_add_email():
    """Test that Record can add an email address."""
    record = Record("John")
    record.add_email("john@example.com")
    assert record.email is not None
    assert record.email.value == "john@example.com"


def test_record_add_email_normalizes_to_lowercase():
    """Test that adding email normalizes to lowercase."""
    record = Record("John")
    record.add_email("JOHN@EXAMPLE.COM")
    assert record.email.value == "john@example.com"


def test_record_add_email_invalid_format_raises_error():
    """Test that adding invalid email raises ValueError."""
    record = Record("John")
    with pytest.raises(ValueError):
        record.add_email("invalid-email")


def test_record_add_email_updates_existing():
    """Test that adding email updates existing email."""
    record = Record("John")
    record.add_email("john@example.com")
    record.add_email("john.new@example.com")
    assert record.email.value == "john.new@example.com"


def test_record_remove_email():
    """Test that Record can remove email address."""
    record = Record("John")
    record.add_email("john@example.com")
    record.remove_email()
    assert record.email is None


def test_record_remove_email_when_not_set():
    """Test that removing email when not set does nothing."""
    record = Record("John")
    record.remove_email()  # Should not raise error
    assert record.email is None


# --- Address Management Tests ---

def test_record_initialization_includes_address():
    """Test that Record initializes with None address."""
    record = Record("John")
    assert record.address is None


def test_record_set_address():
    """Test that Record can set an address."""
    record = Record("John")
    record.set_address("UA", "Kyiv", "Main St 1")
    assert record.address is not None
    assert record.address.country == "UA"
    assert record.address.city == "Kyiv"
    assert record.address.address_line == "Main St 1"


def test_record_set_address_updates_existing():
    """Test that setting address updates existing address."""
    record = Record("John")
    record.set_address("UA", "Kyiv", "Main St 1")
    record.set_address("PL", "Warsaw", "New St 2")
    assert record.address.country == "PL"
    assert record.address.city == "Warsaw"
    assert record.address.address_line == "New St 2"


def test_record_set_address_strips_whitespace():
    """Test that setting address strips whitespace."""
    record = Record("John")
    record.set_address("  UA  ", "  Kyiv  ", "  Main St 1  ")
    assert record.address.country == "UA"
    assert record.address.city == "Kyiv"
    assert record.address.address_line == "Main St 1"


def test_record_remove_address():
    """Test that Record can remove address."""
    record = Record("John")
    record.set_address("UA", "Kyiv", "Main St 1")
    record.remove_address()
    assert record.address is None


def test_record_remove_address_when_not_set():
    """Test that removing address when not set does nothing."""
    record = Record("John")
    record.remove_address()  # Should not raise error
    assert record.address is None


# --- String Representation Tests with Email and Address ---

def test_record_str_representation_with_email():
    """Test that Record string representation includes email."""
    record = Record("John")
    record.add_phone("1234567890")
    record.add_email("john@example.com")
    assert "email: john@example.com" in str(record)


def test_record_str_representation_with_address():
    """Test that Record string representation includes address."""
    record = Record("John")
    record.add_phone("1234567890")
    record.set_address("UA", "Kyiv", "Main St 1")
    assert "address: Main St 1, Kyiv, UA" in str(record)


def test_record_str_representation_with_email_and_address():
    """Test that Record string representation includes both email and address."""
    record = Record("John")
    record.add_phone("1234567890")
    record.add_email("john@example.com")
    record.set_address("UA", "Kyiv", "Main St 1")
    result = str(record)
    assert "email: john@example.com" in result
    assert "address: Main St 1, Kyiv, UA" in result


def test_record_str_representation_with_empty_address():
    """Test that Record string representation excludes empty address."""
    record = Record("John")
    record.add_phone("1234567890")
    record.set_address("", "", "")
    result = str(record)
    assert "address:" not in result


def test_record_str_representation_with_partial_address():
    """Test that Record string representation includes partial address."""
    record = Record("John")
    record.set_address("UA", "Kyiv", "")
    result = str(record)
    assert "address: Kyiv, UA" in result


# --- Backward Compatibility Tests ---

def test_record_setstate_adds_missing_notes():
    """Test that __setstate__ adds missing notes attribute."""
    record = Record("John")
    state = {"name": record.name, "phones": [], "birthday": None, "tags": record.tags}
    record.__setstate__(state)
    assert hasattr(record, "notes")
    assert record.notes == {}


def test_record_setstate_adds_missing_email_and_address():
    """Test that __setstate__ adds missing email and address attributes."""
    record = Record("John")
    state = {"name": record.name, "phones": [], "birthday": None, "tags": record.tags, "notes": {}}
    record.__setstate__(state)
    assert hasattr(record, "email")
    assert record.email is None
    assert hasattr(record, "address")
    assert record.address is None


def test_record_setstate_migrates_old_address_fields():
    """Test that __setstate__ migrates old address fields to Address object."""
    record = Record("John")
    state = {
        "name": record.name,
        "phones": [],
        "birthday": None,
        "tags": record.tags,
        "notes": {},
        "country": "UA",
        "city": "Kyiv",
        "address_line": "Main St 1"
    }
    record.__setstate__(state)
    assert record.address is not None
    assert record.address.country == "UA"
    assert record.address.city == "Kyiv"
    assert record.address.address_line == "Main St 1"
    # Old fields should be removed
    assert not hasattr(record, "country")
    assert not hasattr(record, "city")
    assert not hasattr(record, "address_line")

