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


# --- Backward Compatibility Tests ---

def test_record_setstate_adds_missing_notes():
    """Test that __setstate__ adds missing notes attribute."""
    record = Record("John")
    state = {"name": record.name, "phones": [], "birthday": None, "tags": record.tags}
    record.__setstate__(state)
    assert hasattr(record, "notes")
    assert record.notes == {}

