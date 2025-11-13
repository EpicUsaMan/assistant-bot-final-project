"""
Tests for NoteService.

This module tests all business logic for note operations including
CRUD operations and tag management for notes.
"""

import pytest
from src.models.address_book import AddressBook
from src.models.record import Record
from src.services.note_service import NoteService


@pytest.fixture
def address_book():
    """Create an empty address book for testing."""
    return AddressBook()


@pytest.fixture
def note_service(address_book):
    """Create a note service for testing."""
    return NoteService(address_book)


@pytest.fixture
def populated_service(address_book):
    """Create a note service with some contacts."""
    john = Record("John")
    john.add_phone("1234567890")
    alice = Record("Alice")
    alice.add_phone("0987654321")
    address_book.add_record(john)
    address_book.add_record(alice)
    return NoteService(address_book)


class TestNoteServiceBasics:
    """Test basic note service functionality."""
    
    def test_has_contacts_empty(self, note_service):
        """Test has_contacts returns False for empty address book."""
        assert note_service.has_contacts() is False
    
    def test_has_contacts_with_contacts(self, populated_service):
        """Test has_contacts returns True when contacts exist."""
        assert populated_service.has_contacts() is True
    
    def test_list_contacts_empty(self, note_service):
        """Test list_contacts returns empty list for empty address book."""
        contacts = note_service.list_contacts()
        assert contacts == []
    
    def test_list_contacts_with_data(self, populated_service):
        """Test list_contacts returns sorted contacts."""
        contacts = populated_service.list_contacts()
        assert len(contacts) == 2
        assert contacts[0][0] == "Alice"
        assert contacts[1][0] == "John"
        assert "0987654321" in contacts[0][1]
        assert "1234567890" in contacts[1][1]
    
    def test_list_contacts_without_phones(self, address_book):
        """Test list_contacts handles contacts without phones."""
        bob = Record("Bob")
        address_book.add_record(bob)
        service = NoteService(address_book)
        
        contacts = service.list_contacts()
        assert len(contacts) == 1
        assert contacts[0] == ("Bob", "No phone")


class TestNoteManagement:
    """Test note CRUD operations."""
    
    def test_add_note_to_contact(self, populated_service):
        """Test adding a note to a contact."""
        result = populated_service.add_note("John", "Meeting", "Discuss project timeline")
        
        assert "Meeting" in result
        assert "John" in result
        notes = populated_service.list_notes("John")
        assert len(notes) == 1
        assert notes[0].name == "Meeting"
        assert notes[0].content == "Discuss project timeline"
    
    def test_add_note_without_content(self, populated_service):
        """Test adding a note without content."""
        result = populated_service.add_note("John", "Todo")
        
        assert "Todo" in result
        notes = populated_service.list_notes("John")
        assert len(notes) == 1
        assert notes[0].name == "Todo"
        assert notes[0].content == ""
    
    def test_add_note_to_non_existent_contact(self, note_service):
        """Test adding note to non-existent contact raises error."""
        with pytest.raises(ValueError, match="not found"):
            note_service.add_note("NonExistent", "Meeting", "Content")
    
    def test_add_duplicate_note_raises_error(self, populated_service):
        """Test adding duplicate note raises error."""
        populated_service.add_note("John", "Meeting", "Content 1")
        
        with pytest.raises(ValueError, match="already exists"):
            populated_service.add_note("John", "Meeting", "Content 2")
    
    def test_edit_note(self, populated_service):
        """Test editing a note's content."""
        populated_service.add_note("John", "Meeting", "Original content")
        
        result = populated_service.edit_note("John", "Meeting", "Updated content")
        
        assert "Meeting" in result
        assert "updated" in result.lower()
        note = populated_service.get_note("John", "Meeting")
        assert note.content == "Updated content"
    
    def test_edit_non_existent_note_raises_error(self, populated_service):
        """Test editing non-existent note raises error."""
        with pytest.raises(ValueError, match="not found"):
            populated_service.edit_note("John", "NonExistent", "Content")
    
    def test_edit_note_for_non_existent_contact_raises_error(self, note_service):
        """Test editing note for non-existent contact raises error."""
        with pytest.raises(ValueError, match="not found"):
            note_service.edit_note("NonExistent", "Meeting", "Content")
    
    def test_delete_note(self, populated_service):
        """Test deleting a note."""
        populated_service.add_note("John", "Meeting", "Content")
        
        result = populated_service.delete_note("John", "Meeting")
        
        assert "Meeting" in result
        assert "deleted" in result.lower()
        notes = populated_service.list_notes("John")
        assert len(notes) == 0
    
    def test_delete_non_existent_note_raises_error(self, populated_service):
        """Test deleting non-existent note raises error."""
        with pytest.raises(ValueError, match="not found"):
            populated_service.delete_note("John", "NonExistent")
    
    def test_delete_note_for_non_existent_contact_raises_error(self, note_service):
        """Test deleting note for non-existent contact raises error."""
        with pytest.raises(ValueError, match="not found"):
            note_service.delete_note("NonExistent", "Meeting")
    
    def test_list_notes(self, populated_service):
        """Test listing all notes for a contact."""
        populated_service.add_note("John", "Meeting", "Content 1")
        populated_service.add_note("John", "Todo", "Content 2")
        
        notes = populated_service.list_notes("John")
        
        assert len(notes) == 2
        note_names = [n.name for n in notes]
        assert "Meeting" in note_names
        assert "Todo" in note_names
    
    def test_list_notes_empty(self, populated_service):
        """Test listing notes when contact has no notes."""
        notes = populated_service.list_notes("John")
        assert notes == []
    
    def test_list_notes_for_non_existent_contact_raises_error(self, note_service):
        """Test listing notes for non-existent contact raises error."""
        with pytest.raises(ValueError, match="not found"):
            note_service.list_notes("NonExistent")
    
    def test_get_note(self, populated_service):
        """Test getting a specific note."""
        populated_service.add_note("John", "Meeting", "Important meeting")
        
        note = populated_service.get_note("John", "Meeting")
        
        assert note.name == "Meeting"
        assert note.content == "Important meeting"
    
    def test_get_non_existent_note_raises_error(self, populated_service):
        """Test getting non-existent note raises error."""
        with pytest.raises(ValueError, match="not found"):
            populated_service.get_note("John", "NonExistent")
    
    def test_get_note_for_non_existent_contact_raises_error(self, note_service):
        """Test getting note for non-existent contact raises error."""
        with pytest.raises(ValueError, match="not found"):
            note_service.get_note("NonExistent", "Meeting")


class TestNoteTagManagement:
    """Test tag management for notes."""
    
    def test_add_tag_to_note(self, populated_service):
        """Test adding a tag to a note."""
        populated_service.add_note("John", "Meeting", "Content")
        
        result = populated_service.note_add_tag("John", "Meeting", "important")
        
        assert "important" in result
        assert "Meeting" in result
        tags = populated_service.note_list_tags("John", "Meeting")
        assert "important" in tags
    
    def test_add_tag_normalizes_to_lowercase(self, populated_service):
        """Test that tags are normalized to lowercase."""
        populated_service.add_note("John", "Meeting", "Content")
        
        result = populated_service.note_add_tag("John", "Meeting", "Important")
        
        assert "important" in result
        tags = populated_service.note_list_tags("John", "Meeting")
        assert "important" in tags
        assert "Important" not in tags
    
    def test_add_invalid_tag_to_note_raises_error(self, populated_service):
        """Test adding invalid tag to note raises error."""
        populated_service.add_note("John", "Meeting", "Content")
        
        with pytest.raises(ValueError, match="Invalid tag"):
            populated_service.note_add_tag("John", "Meeting", "Invalid Tag!")
    
    def test_add_tag_to_non_existent_note_raises_error(self, populated_service):
        """Test adding tag to non-existent note raises error."""
        with pytest.raises(ValueError, match="not found"):
            populated_service.note_add_tag("John", "NonExistent", "important")
    
    def test_add_tag_for_non_existent_contact_raises_error(self, note_service):
        """Test adding tag for non-existent contact raises error."""
        with pytest.raises(ValueError, match="not found"):
            note_service.note_add_tag("NonExistent", "Meeting", "important")
    
    def test_remove_tag_from_note(self, populated_service):
        """Test removing a tag from a note."""
        populated_service.add_note("John", "Meeting", "Content")
        populated_service.note_add_tag("John", "Meeting", "important")
        populated_service.note_add_tag("John", "Meeting", "work")
        
        result = populated_service.note_remove_tag("John", "Meeting", "important")
        
        assert "important" in result
        assert "removed" in result.lower()
        tags = populated_service.note_list_tags("John", "Meeting")
        assert "important" not in tags
        assert "work" in tags
    
    def test_remove_tag_from_non_existent_note_raises_error(self, populated_service):
        """Test removing tag from non-existent note raises error."""
        with pytest.raises(ValueError, match="not found"):
            populated_service.note_remove_tag("John", "NonExistent", "important")
    
    def test_remove_tag_for_non_existent_contact_raises_error(self, note_service):
        """Test removing tag for non-existent contact raises error."""
        with pytest.raises(ValueError, match="not found"):
            note_service.note_remove_tag("NonExistent", "Meeting", "important")
    
    def test_clear_tags_from_note(self, populated_service):
        """Test clearing all tags from a note."""
        populated_service.add_note("John", "Meeting", "Content")
        populated_service.note_add_tag("John", "Meeting", "important")
        populated_service.note_add_tag("John", "Meeting", "work")
        
        result = populated_service.note_clear_tags("John", "Meeting")
        
        assert "cleared" in result.lower()
        assert "Meeting" in result
        tags = populated_service.note_list_tags("John", "Meeting")
        assert tags == []
    
    def test_clear_tags_from_non_existent_note_raises_error(self, populated_service):
        """Test clearing tags from non-existent note raises error."""
        with pytest.raises(ValueError, match="not found"):
            populated_service.note_clear_tags("John", "NonExistent")
    
    def test_clear_tags_for_non_existent_contact_raises_error(self, note_service):
        """Test clearing tags for non-existent contact raises error."""
        with pytest.raises(ValueError, match="not found"):
            note_service.note_clear_tags("NonExistent", "Meeting")
    
    def test_list_tags_for_note(self, populated_service):
        """Test listing all tags for a note."""
        populated_service.add_note("John", "Meeting", "Content")
        populated_service.note_add_tag("John", "Meeting", "important")
        populated_service.note_add_tag("John", "Meeting", "work")
        populated_service.note_add_tag("John", "Meeting", "urgent")
        
        tags = populated_service.note_list_tags("John", "Meeting")
        
        assert len(tags) == 3
        assert "important" in tags
        assert "work" in tags
        assert "urgent" in tags
    
    def test_list_tags_for_note_without_tags(self, populated_service):
        """Test listing tags for note without tags."""
        populated_service.add_note("John", "Meeting", "Content")
        
        tags = populated_service.note_list_tags("John", "Meeting")
        
        assert tags == []
    
    def test_list_tags_for_non_existent_note_raises_error(self, populated_service):
        """Test listing tags for non-existent note raises error."""
        with pytest.raises(ValueError, match="not found"):
            populated_service.note_list_tags("John", "NonExistent")
    
    def test_list_tags_for_non_existent_contact_raises_error(self, note_service):
        """Test listing tags for non-existent contact raises error."""
        with pytest.raises(ValueError, match="not found"):
            note_service.note_list_tags("NonExistent", "Meeting")

