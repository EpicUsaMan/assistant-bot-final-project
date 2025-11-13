"""Tests for search commands module."""

import pytest
from unittest.mock import Mock
from typer.testing import CliRunner
import click

from src.commands.search import (
    _search_contacts_impl,
    _search_notes_impl,
    display_contact_results_tree,
    display_note_results_tree,
)
from src.services.search_service import ContactSearchType, NoteSearchType
from src.models.note import Note
from src.main import container


runner = CliRunner()


@pytest.fixture
def mock_search_service():
    """Create a mock search service."""
    return Mock()


@pytest.fixture
def mock_record():
    """Create a mock record."""
    record = Mock()
    record.phones = []
    record.birthday = None
    record.email = None
    record.tags_list.return_value = []
    record.list_notes.return_value = []
    return record


class TestSearchContactsImpl:
    """Tests for _search_contacts_impl function."""
    
    def test_search_contacts_by_name(self, mock_search_service, mock_record):
        """Test searching contacts by name."""
        mock_search_service.search_contacts.return_value = [("John", mock_record)]
        
        _search_contacts_impl("john", "name", service=mock_search_service)
        
        mock_search_service.search_contacts.assert_called_once_with(
            "john", ContactSearchType.NAME
        )
    
    def test_search_contacts_by_phone(self, mock_search_service, mock_record):
        """Test searching contacts by phone."""
        mock_search_service.search_contacts.return_value = [("John", mock_record)]
        
        with container.search_service.override(mock_search_service):
            _search_contacts_impl("1234", "phone")
        
        mock_search_service.search_contacts.assert_called_once_with(
            "1234", ContactSearchType.PHONE
        )
    
    def test_search_contacts_by_all(self, mock_search_service, mock_record):
        """Test searching contacts in all fields."""
        mock_search_service.search_contacts.return_value = [("John", mock_record)]
        
        with container.search_service.override(mock_search_service):
            _search_contacts_impl("john", "all")
        
        mock_search_service.search_contacts.assert_called_once_with(
            "john", ContactSearchType.ALL
        )
    
    def test_search_contacts_by_tags(self, mock_search_service, mock_record):
        """Test searching contacts by tags."""
        mock_search_service.search_contacts.return_value = [("John", mock_record)]
        
        with container.search_service.override(mock_search_service):
            _search_contacts_impl("work", "tags")
        
        mock_search_service.search_contacts.assert_called_once_with(
            "work", ContactSearchType.TAGS
        )
    
    def test_search_contacts_by_tags_all(self, mock_search_service, mock_record):
        """Test searching contacts with all specified tags."""
        mock_search_service.search_contacts.return_value = [("John", mock_record)]
        
        with container.search_service.override(mock_search_service):
            _search_contacts_impl("work,important", "tags-all")
        
        mock_search_service.search_contacts.assert_called_once_with(
            "work,important", ContactSearchType.TAGS_ALL
        )
    
    def test_search_contacts_by_tags_any(self, mock_search_service, mock_record):
        """Test searching contacts with any of specified tags."""
        mock_search_service.search_contacts.return_value = [("John", mock_record)]
        
        with container.search_service.override(mock_search_service):
            _search_contacts_impl("work,personal", "tags-any")
        
        mock_search_service.search_contacts.assert_called_once_with(
            "work,personal", ContactSearchType.TAGS_ANY
        )
    
    def test_search_contacts_by_notes_text(self, mock_search_service, mock_record):
        """Test searching contacts by note content."""
        mock_search_service.search_contacts.return_value = [("John", mock_record)]
        
        with container.search_service.override(mock_search_service):
            _search_contacts_impl("meeting", "notes-text")
        
        mock_search_service.search_contacts.assert_called_once_with(
            "meeting", ContactSearchType.NOTES_TEXT
        )
    
    def test_search_contacts_by_notes_name(self, mock_search_service, mock_record):
        """Test searching contacts by note names."""
        mock_search_service.search_contacts.return_value = [("John", mock_record)]
        
        with container.search_service.override(mock_search_service):
            _search_contacts_impl("Todo", "notes-name")
        
        mock_search_service.search_contacts.assert_called_once_with(
            "Todo", ContactSearchType.NOTES_NAME
        )
    
    def test_search_contacts_by_notes_tags(self, mock_search_service, mock_record):
        """Test searching contacts by note tags."""
        mock_search_service.search_contacts.return_value = [("John", mock_record)]
        
        with container.search_service.override(mock_search_service):
            _search_contacts_impl("important", "notes-tags")
        
        mock_search_service.search_contacts.assert_called_once_with(
            "important", ContactSearchType.NOTES_TAGS
        )
    
    def test_search_contacts_invalid_type_raises_error(self, mock_search_service):
        """Test searching with invalid type raises error."""
        with pytest.raises(click.exceptions.Exit):
            _search_contacts_impl("query", "invalid_type", service=mock_search_service)


class TestSearchNotesImpl:
    """Tests for _search_notes_impl function."""
    
    def test_search_notes_by_name(self, mock_search_service):
        """Test searching notes by name."""
        note = Note("Meeting", "Content")
        mock_search_service.search_notes.return_value = [("John", "Meeting", note)]
        
        with container.search_service.override(mock_search_service):
            _search_notes_impl("meeting", "name")
        
        mock_search_service.search_notes.assert_called_once_with(
            "meeting", NoteSearchType.NAME
        )
    
    def test_search_notes_by_text(self, mock_search_service):
        """Test searching notes by content."""
        note = Note("Meeting", "Discuss project")
        mock_search_service.search_notes.return_value = [("John", "Meeting", note)]
        
        with container.search_service.override(mock_search_service):
            _search_notes_impl("project", "text")
        
        mock_search_service.search_notes.assert_called_once_with(
            "project", NoteSearchType.TEXT
        )
    
    def test_search_notes_by_all(self, mock_search_service):
        """Test searching notes in all fields."""
        note = Note("Meeting", "Content")
        mock_search_service.search_notes.return_value = [("John", "Meeting", note)]
        
        with container.search_service.override(mock_search_service):
            _search_notes_impl("query", "all")
        
        mock_search_service.search_notes.assert_called_once_with(
            "query", NoteSearchType.ALL
        )
    
    def test_search_notes_by_tags(self, mock_search_service):
        """Test searching notes by tags."""
        note = Note("Meeting", "Content")
        note.tags.add("work")
        mock_search_service.search_notes.return_value = [("John", "Meeting", note)]
        
        with container.search_service.override(mock_search_service):
            _search_notes_impl("work", "tags")
        
        mock_search_service.search_notes.assert_called_once_with(
            "work", NoteSearchType.TAGS
        )
    
    def test_search_notes_by_contact_name(self, mock_search_service):
        """Test searching notes by contact name."""
        note = Note("Meeting", "Content")
        mock_search_service.search_notes.return_value = [("John", "Meeting", note)]
        
        with container.search_service.override(mock_search_service):
            _search_notes_impl("john", "contact-name")
        
        mock_search_service.search_notes.assert_called_once_with(
            "john", NoteSearchType.CONTACT_NAME
        )
    
    def test_search_notes_by_contact_phone(self, mock_search_service):
        """Test searching notes by contact phone."""
        note = Note("Meeting", "Content")
        mock_search_service.search_notes.return_value = [("John", "Meeting", note)]
        
        with container.search_service.override(mock_search_service):
            _search_notes_impl("1234", "contact-phone")
        
        mock_search_service.search_notes.assert_called_once_with(
            "1234", NoteSearchType.CONTACT_PHONE
        )
    
    def test_search_notes_by_contact_tags(self, mock_search_service):
        """Test searching notes by contact tags."""
        note = Note("Meeting", "Content")
        mock_search_service.search_notes.return_value = [("John", "Meeting", note)]
        
        with container.search_service.override(mock_search_service):
            _search_notes_impl("important", "contact-tags")
        
        mock_search_service.search_notes.assert_called_once_with(
            "important", NoteSearchType.CONTACT_TAGS
        )
    
    def test_search_notes_invalid_type_raises_error(self, mock_search_service):
        """Test searching with invalid type raises error."""
        with pytest.raises(click.exceptions.Exit):
            _search_notes_impl("query", "invalid_type", service=mock_search_service)


class TestDisplayContactResultsTree:
    """Tests for display_contact_results_tree function."""
    
    def test_display_empty_results(self, mock_record):
        """Test displaying empty search results."""
        display_contact_results_tree([], "query", "name")
        # Should not raise any errors
    
    def test_display_results_with_phones(self, mock_record):
        """Test displaying results with phone numbers."""
        phone_mock = Mock()
        phone_mock.value = "1234567890"
        mock_record.phones = [phone_mock]
        
        display_contact_results_tree([("John", mock_record)], "query", "name")
        # Should not raise any errors
    
    def test_display_results_with_birthday(self, mock_record):
        """Test displaying results with birthday."""
        mock_record.birthday = Mock()
        mock_record.birthday.__str__ = Mock(return_value="01.01.2000")
        
        display_contact_results_tree([("John", mock_record)], "query", "name")
        # Should not raise any errors
    
    def test_display_results_with_tags(self, mock_record):
        """Test displaying results with tags."""
        mock_record.tags_list.return_value = ["work", "important"]
        
        display_contact_results_tree([("John", mock_record)], "query", "name")
        # Should not raise any errors
    
    def test_display_results_with_notes(self, mock_record):
        """Test displaying results with notes."""
        note = Note("Meeting", "Content")
        mock_record.list_notes.return_value = [note]
        
        display_contact_results_tree([("John", mock_record)], "query", "name")
        # Should not raise any errors
    
    def test_display_results_with_many_notes(self, mock_record):
        """Test displaying results with many notes (truncation)."""
        notes = [Note(f"Note{i}", f"Content{i}") for i in range(5)]
        mock_record.list_notes.return_value = notes
        
        display_contact_results_tree([("John", mock_record)], "query", "name")
        # Should not raise any errors


class TestDisplayNoteResultsTree:
    """Tests for display_note_results_tree function."""
    
    def test_display_empty_results(self):
        """Test displaying empty note search results."""
        display_note_results_tree([], "query", "text")
        # Should not raise any errors
    
    def test_display_results_with_content(self):
        """Test displaying note results with content."""
        note = Note("Meeting", "Discuss project timeline")
        results = [("John", "Meeting", note)]
        
        display_note_results_tree(results, "query", "text")
        # Should not raise any errors
    
    def test_display_results_without_content(self):
        """Test displaying note results without content."""
        note = Note("Meeting", "")
        results = [("John", "Meeting", note)]
        
        display_note_results_tree(results, "query", "name")
        # Should not raise any errors
    
    def test_display_results_with_tags(self):
        """Test displaying note results with tags."""
        note = Note("Meeting", "Content")
        note.tags.add("work")
        note.tags.add("important")
        results = [("John", "Meeting", note)]
        
        display_note_results_tree(results, "query", "tags")
        # Should not raise any errors
    
    def test_display_results_multiple_contacts(self):
        """Test displaying note results from multiple contacts."""
        note1 = Note("Meeting", "Content 1")
        note2 = Note("Todo", "Content 2")
        results = [
            ("John", "Meeting", note1),
            ("Alice", "Todo", note2)
        ]
        
        display_note_results_tree(results, "query", "all")
        # Should not raise any errors
    
    def test_display_results_long_content(self):
        """Test displaying note results with long content (truncation)."""
        long_content = "a" * 100
        note = Note("Meeting", long_content)
        results = [("John", "Meeting", note)]
        
        display_note_results_tree(results, "query", "text")
        # Should not raise any errors

