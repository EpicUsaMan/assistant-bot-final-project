"""Tests for notes commands module."""

import pytest
from unittest.mock import Mock, patch
from typer.testing import CliRunner
import click

from src.commands.notes import (
    app,
    _add_note_impl,
    _edit_note_impl,
    _delete_note_impl,
    _list_notes_impl,
    _show_note_impl,
    _note_tag_add_impl,
    _note_tag_remove_impl,
    _note_tag_clear_impl,
    _note_tag_list_impl,
)
from src.models.note import Note
from src.main import container


runner = CliRunner()


@pytest.fixture
def mock_note_service():
    """Create a mock note service."""
    service = Mock()
    service.has_contacts.return_value = True
    service.list_contacts.return_value = [("John", Mock())]
    return service


class TestAddNoteImpl:
    """Tests for _add_note_impl function."""
    
    def test_add_note_success(self, mock_note_service):
        """Test adding a note successfully."""
        mock_note_service.add_note.return_value = "Note 'Meeting' added to John."
        
        _add_note_impl("John", "Meeting", "Discuss project", service=mock_note_service, filename="test.pkl")
        
        mock_note_service.add_note.assert_called_once_with("John", "Meeting", "Discuss project")


class TestEditNoteImpl:
    """Tests for _edit_note_impl function."""
    
    def test_edit_note_success(self, mock_note_service):
        """Test editing a note successfully."""
        mock_note_service.edit_note.return_value = "Note 'Meeting' updated for John."
        
        _edit_note_impl("John", "Meeting", "New content", service=mock_note_service, filename="test.pkl")
        
        mock_note_service.edit_note.assert_called_once_with("John", "Meeting", "New content")


class TestDeleteNoteImpl:
    """Tests for _delete_note_impl function."""
    
    def test_delete_note_success(self, mock_note_service):
        """Test deleting a note successfully."""
        mock_note_service.delete_note.return_value = "Note 'Meeting' deleted from John."
        
        _delete_note_impl("John", "Meeting", service=mock_note_service, filename="test.pkl")
        
        mock_note_service.delete_note.assert_called_once_with("John", "Meeting")


class TestListNotesImpl:
    """Tests for _list_notes_impl function."""
    
    def test_list_notes_with_notes(self, mock_note_service):
        """Test listing notes when contact has notes."""
        note1 = Note("Meeting", "Discuss project")
        note2 = Note("Todo", "Buy groceries")
        mock_note_service.list_notes.return_value = [note1, note2]
        
        _list_notes_impl("John", service=mock_note_service)
        
        mock_note_service.list_notes.assert_called_once_with("John")
    
    def test_list_notes_empty(self, mock_note_service):
        """Test listing notes when contact has no notes."""
        mock_note_service.list_notes.return_value = []
        
        _list_notes_impl("John", service=mock_note_service)
        
        mock_note_service.list_notes.assert_called_once_with("John")


class TestShowNoteImpl:
    """Tests for _show_note_impl function."""
    
    def test_show_note_with_content(self, mock_note_service):
        """Test showing a note with content."""
        note = Note("Meeting", "Discuss project timeline")
        mock_note_service.get_note.return_value = note
        
        _show_note_impl("John", "Meeting", service=mock_note_service)
        
        mock_note_service.get_note.assert_called_once_with("John", "Meeting")
    
    def test_show_note_empty_content(self, mock_note_service):
        """Test showing a note with empty content."""
        note = Note("Meeting", "")
        mock_note_service.get_note.return_value = note
        
        _show_note_impl("John", "Meeting", service=mock_note_service)
        
        mock_note_service.get_note.assert_called_once_with("John", "Meeting")
    
    def test_show_note_with_tags(self, mock_note_service):
        """Test showing a note with tags."""
        note = Note("Meeting", "Content")
        note.tags.add("work")
        note.tags.add("important")
        mock_note_service.get_note.return_value = note
        
        _show_note_impl("John", "Meeting", service=mock_note_service)
        
        mock_note_service.get_note.assert_called_once_with("John", "Meeting")


class TestNoteTagAddImpl:
    """Tests for _note_tag_add_impl function."""
    
    def test_add_single_tag(self, mock_note_service):
        """Test adding a single tag to a note."""
        mock_note_service.note_add_tag.return_value = "Tag 'work' added."
        
        _note_tag_add_impl("John", "Meeting", ["work"], service=mock_note_service, filename="test.pkl")
        
        mock_note_service.note_add_tag.assert_called_once_with("John", "Meeting", "work")
    
    def test_add_multiple_tags(self, mock_note_service):
        """Test adding multiple tags to a note."""
        mock_note_service.note_add_tag.return_value = "Tag added."
        
        _note_tag_add_impl("John", "Meeting", ["work", "important"], service=mock_note_service, filename="test.pkl")
        
        assert mock_note_service.note_add_tag.call_count == 2
    
    def test_add_invalid_tag_raises_error(self, mock_note_service):
        """Test adding invalid tag raises error."""
        with pytest.raises(click.exceptions.Exit):
            _note_tag_add_impl("John", "Meeting", [""], service=mock_note_service, filename="test.pkl")


class TestNoteTagRemoveImpl:
    """Tests for _note_tag_remove_impl function."""
    
    def test_remove_tag(self, mock_note_service):
        """Test removing a tag from a note."""
        mock_note_service.note_remove_tag.return_value = "Tag 'work' removed."
        
        _note_tag_remove_impl("John", "Meeting", "work", service=mock_note_service, filename="test.pkl")
        
        mock_note_service.note_remove_tag.assert_called_once_with("John", "Meeting", "work")


class TestNoteTagClearImpl:
    """Tests for _note_tag_clear_impl function."""
    
    def test_clear_tags(self, mock_note_service):
        """Test clearing all tags from a note."""
        mock_note_service.note_clear_tags.return_value = "All tags cleared."
        
        _note_tag_clear_impl("John", "Meeting", service=mock_note_service, filename="test.pkl")
        
        mock_note_service.note_clear_tags.assert_called_once_with("John", "Meeting")


class TestNoteTagListImpl:
    """Tests for _note_tag_list_impl function."""
    
    def test_list_tags_with_tags(self, mock_note_service):
        """Test listing tags when note has tags."""
        mock_note_service.note_list_tags.return_value = ["work", "important"]
        
        _note_tag_list_impl("John", "Meeting", service=mock_note_service)
        
        mock_note_service.note_list_tags.assert_called_once_with("John", "Meeting")
    
    def test_list_tags_empty(self, mock_note_service):
        """Test listing tags when note has no tags."""
        mock_note_service.note_list_tags.return_value = []
        
        _note_tag_list_impl("John", "Meeting", service=mock_note_service)
        
        mock_note_service.note_list_tags.assert_called_once_with("John", "Meeting")

