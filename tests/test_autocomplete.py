"""
Tests for autocomplete utility functions.

This module tests the autocomplete helper functions used for
shell completion and REPL completion.
"""

import pytest
from src.models.address_book import AddressBook
from src.models.record import Record
from src.services.note_service import NoteService
from src.utils.autocomplete import (
    _complete_contact_name_impl,
    _complete_note_name_impl,
    _complete_tag_impl,
    complete_contact_name,
    complete_note_name,
    complete_tag,
)


@pytest.fixture
def note_service():
    """Create a note service with test data."""
    book = AddressBook()
    
    john = Record("John Doe")
    john.add_phone("1234567890")
    john.add_note("Meeting", "Discuss Q4 targets")
    john.add_note("Todo", "Follow up on email")
    john.note_add_tag("Meeting", "work")
    john.note_add_tag("Meeting", "urgent")
    john.note_add_tag("Todo", "personal")
    book.add_record(john)
    
    alice = Record("Alice Smith")
    alice.add_phone("0987654321")
    alice.add_note("Ideas", "New project ideas")
    alice.note_add_tag("Ideas", "creative")
    alice.note_add_tag("Ideas", "work")
    book.add_record(alice)
    
    bob = Record("Bob Johnson")
    bob.add_phone("5551234567")
    book.add_record(bob)
    
    return NoteService(book)


class TestCompleteContactName:
    """Tests for contact name autocomplete."""
    
    def test_complete_contact_name_impl_all_contacts(self, note_service):
        """Test getting all contact names without filter."""
        result = _complete_contact_name_impl("", service=note_service)
        assert len(result) == 3
        assert result == ["Alice Smith", "Bob Johnson", "John Doe"]
    
    def test_complete_contact_name_impl_with_prefix(self, note_service):
        """Test filtering contacts by prefix."""
        result = _complete_contact_name_impl("j", service=note_service)
        assert result == ["John Doe"]
    
    def test_complete_contact_name_impl_case_insensitive(self, note_service):
        """Test that filtering is case insensitive."""
        result = _complete_contact_name_impl("ALICE", service=note_service)
        assert result == ["Alice Smith"]
    
    def test_complete_contact_name_impl_no_matches(self, note_service):
        """Test with prefix that matches no contacts."""
        result = _complete_contact_name_impl("xyz", service=note_service)
        assert result == []
    
    def test_complete_contact_name_impl_empty_service(self):
        """Test with empty address book."""
        empty_service = NoteService(AddressBook())
        result = _complete_contact_name_impl("", service=empty_service)
        assert result == []
    
    def test_complete_contact_name_wrapper(self, note_service, monkeypatch):
        """Test the wrapper function calls impl correctly."""
        # Mock the impl function
        called_with = []
        def mock_impl(incomplete, service=None):
            called_with.append(incomplete)
            return ["test"]
        
        monkeypatch.setattr("src.utils.autocomplete._complete_contact_name_impl", mock_impl)
        
        result = complete_contact_name(incomplete="john")
        assert result == ["test"]
        assert called_with == ["john"]


class TestCompleteNoteName:
    """Tests for note name autocomplete."""
    
    def test_complete_note_name_impl_for_specific_contact(self, note_service):
        """Test getting notes for a specific contact."""
        result = _complete_note_name_impl("", "John Doe", service=note_service)
        assert len(result) == 2
        assert "Meeting" in result
        assert "Todo" in result
    
    def test_complete_note_name_impl_all_notes(self, note_service):
        """Test getting all notes from all contacts."""
        result = _complete_note_name_impl("", None, service=note_service)
        assert len(result) == 3
        assert "Meeting" in result
        assert "Todo" in result
        assert "Ideas" in result
    
    def test_complete_note_name_impl_with_prefix(self, note_service):
        """Test filtering notes by prefix."""
        result = _complete_note_name_impl("m", None, service=note_service)
        assert result == ["Meeting"]
    
    def test_complete_note_name_impl_case_insensitive(self, note_service):
        """Test that filtering is case insensitive."""
        result = _complete_note_name_impl("TODO", None, service=note_service)
        assert result == ["Todo"]
    
    def test_complete_note_name_impl_no_matches(self, note_service):
        """Test with prefix that matches no notes."""
        result = _complete_note_name_impl("xyz", None, service=note_service)
        assert result == []
    
    def test_complete_note_name_impl_non_existent_contact(self, note_service):
        """Test with non-existent contact returns empty list."""
        result = _complete_note_name_impl("", "NonExistent", service=note_service)
        assert result == []
    
    def test_complete_note_name_impl_contact_without_notes(self, note_service):
        """Test with contact that has no notes."""
        result = _complete_note_name_impl("", "Bob Johnson", service=note_service)
        assert result == []
    
    def test_complete_note_name_wrapper_with_context(self, note_service, monkeypatch):
        """Test wrapper extracts contact_name from context."""
        from click import Context, Command
        
        called_with = []
        def mock_impl(incomplete, contact_name, service=None):
            called_with.append((incomplete, contact_name))
            return ["test"]
        
        monkeypatch.setattr("src.utils.autocomplete._complete_note_name_impl", mock_impl)
        
        # Create context with params
        ctx = Context(Command("test"))
        ctx.params = {"contact_name": "John Doe"}
        
        result = complete_note_name(ctx=ctx, incomplete="m")
        assert result == ["test"]
        assert called_with == [("m", "John Doe")]
    
    def test_complete_note_name_wrapper_without_context(self, note_service, monkeypatch):
        """Test wrapper works without context."""
        called_with = []
        def mock_impl(incomplete, contact_name, service=None):
            called_with.append((incomplete, contact_name))
            return ["test"]
        
        monkeypatch.setattr("src.utils.autocomplete._complete_note_name_impl", mock_impl)
        
        result = complete_note_name(incomplete="m")
        assert result == ["test"]
        assert called_with == [("m", None)]


class TestCompleteTag:
    """Tests for tag autocomplete."""
    
    def test_complete_tag_impl_for_specific_note(self, note_service):
        """Test getting tags for a specific note."""
        result = _complete_tag_impl("", "John Doe", "Meeting", service=note_service)
        assert len(result) == 2
        assert "urgent" in result
        assert "work" in result
    
    def test_complete_tag_impl_for_contact_all_notes(self, note_service):
        """Test getting all tags from all notes of a contact."""
        result = _complete_tag_impl("", "John Doe", None, service=note_service)
        # John has Meeting(work, urgent) and Todo(personal)
        assert len(result) >= 2  # At least work and urgent or personal
        # Check at least one tag is present
        assert any(tag in result for tag in ["work", "urgent", "personal"])
    
    def test_complete_tag_impl_all_tags(self, note_service):
        """Test getting all tags from all notes in all contacts."""
        result = _complete_tag_impl("", None, None, service=note_service)
        # All contacts: John(work, urgent, personal) + Alice(creative, work)
        assert len(result) >= 3  # At least a few tags
        # Check some tags are present
        assert any(tag in result for tag in ["work", "creative"])
    
    def test_complete_tag_impl_with_prefix(self, note_service):
        """Test filtering tags by prefix."""
        result = _complete_tag_impl("w", None, None, service=note_service)
        # Should include "work" which starts with 'w'
        assert "work" in result
        # Should not include tags that don't start with 'w'
        assert "creative" not in result
    
    def test_complete_tag_impl_case_insensitive(self, note_service):
        """Test that filtering is case insensitive."""
        result = _complete_tag_impl("WORK", None, None, service=note_service)
        # Should match "work" case-insensitively
        assert "work" in result or len(result) >= 1
    
    def test_complete_tag_impl_no_matches(self, note_service):
        """Test with prefix that matches no tags."""
        result = _complete_tag_impl("xyz", None, None, service=note_service)
        assert result == []
    
    def test_complete_tag_impl_non_existent_contact(self, note_service):
        """Test with non-existent contact returns empty list."""
        result = _complete_tag_impl("", "NonExistent", "Meeting", service=note_service)
        assert result == []
    
    def test_complete_tag_impl_non_existent_note(self, note_service):
        """Test with non-existent note returns empty list."""
        result = _complete_tag_impl("", "John Doe", "NonExistent", service=note_service)
        assert result == []
    
    def test_complete_tag_impl_contact_without_notes(self, note_service):
        """Test with contact that has no notes."""
        result = _complete_tag_impl("", "Bob Johnson", None, service=note_service)
        assert result == []
    
    def test_complete_tag_wrapper_with_full_context(self, note_service, monkeypatch):
        """Test wrapper extracts both contact_name and note_name from context."""
        from click import Context, Command
        
        called_with = []
        def mock_impl(incomplete, contact_name, note_name, service=None):
            called_with.append((incomplete, contact_name, note_name))
            return ["test"]
        
        monkeypatch.setattr("src.utils.autocomplete._complete_tag_impl", mock_impl)
        
        # Create context with params
        ctx = Context(Command("test"))
        ctx.params = {"contact_name": "John Doe", "note_name": "Meeting"}
        
        result = complete_tag(ctx=ctx, incomplete="w")
        assert result == ["test"]
        assert called_with == [("w", "John Doe", "Meeting")]
    
    def test_complete_tag_wrapper_without_context(self, note_service, monkeypatch):
        """Test wrapper works without context."""
        called_with = []
        def mock_impl(incomplete, contact_name, note_name, service=None):
            called_with.append((incomplete, contact_name, note_name))
            return ["test"]
        
        monkeypatch.setattr("src.utils.autocomplete._complete_tag_impl", mock_impl)
        
        result = complete_tag(incomplete="w")
        assert result == ["test"]
        assert called_with == [("w", None, None)]


class TestAutocompleteErrorHandling:
    """Tests for error handling in autocomplete functions."""
    
    def test_complete_contact_name_impl_handles_exceptions(self, monkeypatch):
        """Test that exceptions are caught and empty list returned."""
        # Create service that will raise exception
        bad_service = NoteService(AddressBook())
        
        # Mock has_contacts to raise exception
        def bad_has_contacts():
            raise RuntimeError("Test error")
        
        monkeypatch.setattr(bad_service, "has_contacts", bad_has_contacts)
        
        result = _complete_contact_name_impl("", service=bad_service)
        assert result == []
    
    def test_complete_note_name_impl_handles_exceptions(self, monkeypatch):
        """Test that exceptions in note listing are handled."""
        bad_service = NoteService(AddressBook())
        
        # Mock list_contacts to raise exception
        def bad_list_contacts():
            raise RuntimeError("Test error")
        
        monkeypatch.setattr(bad_service, "list_contacts", bad_list_contacts)
        
        result = _complete_note_name_impl("", None, service=bad_service)
        assert result == []
    
    def test_complete_tag_impl_handles_exceptions(self, monkeypatch):
        """Test that exceptions in tag listing are handled."""
        bad_service = NoteService(AddressBook())
        
        # Mock list_contacts to raise exception
        def bad_list_contacts():
            raise RuntimeError("Test error")
        
        monkeypatch.setattr(bad_service, "list_contacts", bad_list_contacts)
        
        result = _complete_tag_impl("", None, None, service=bad_service)
        assert result == []

