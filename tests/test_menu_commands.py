"""
Tests for interactive menu commands (search.py and notes_menu.py).

Since these commands use questionary for interactive prompts, we test their
underlying helper functions and service integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from rich.console import Console

from src.services.contact_service import ContactService
from src.services.search_service import ContactSearchType, NoteSearchType
from src.models.address_book import AddressBook
from src.models.record import Record
from src.commands.search import display_contact_results_tree, display_note_results_tree


class TestSearchMenuHelpers:
    """Test helper functions in the search menu command."""
    
    @pytest.fixture
    def mock_console(self):
        """Fixture for a mock console."""
        return Mock(spec=Console)
    
    @pytest.fixture
    def sample_contact_results(self):
        """Fixture for sample contact search results."""
        record1 = Record("Alice")
        record1.add_phone("1234567890")
        record1.add_tag("ai")
        
        record2 = Record("Bob")
        record2.add_phone("9876543210")
        
        return [("Alice", record1), ("Bob", record2)]
    
    @pytest.fixture
    def sample_note_results(self):
        """Fixture for sample note search results."""
        record = Record("Alice")
        record.add_note("Ideas", "Revolutionary concept")
        note = record.find_note("Ideas")
        note.add_tag("innovation")
        
        return [("Alice", "Ideas", note)]
    
    @patch('src.commands.search.console')
    def test_display_contact_results_shows_results(self, mock_console, sample_contact_results):
        """Test that display_contact_results shows results in a tree."""
        display_contact_results_tree(sample_contact_results, "alice", "all")
        
        # Should print a table, not a "not found" message
        assert mock_console.print.called
        call_args = mock_console.print.call_args
        # The first argument should be a Table object (not a string with "No contacts")
        printed_obj = call_args[0][0]
        assert not isinstance(printed_obj, str) or "No contacts found" not in printed_obj
    
    @patch('src.commands.search.console')
    def test_display_contact_results_shows_no_results_message(self, mock_console):
        """Test that display_contact_results shows message when no results."""
        display_contact_results_tree([], "nonexistent", "all")
        
        # Should print "No contacts found" message
        assert mock_console.print.called
        call_args = mock_console.print.call_args[0][0]
        assert "No contacts found" in call_args
        assert "nonexistent" in call_args
    
    @patch('src.commands.search.console')
    def test_display_note_results_shows_results(self, mock_console, sample_note_results):
        """Test that display_note_results shows results in a tree."""
        display_note_results_tree(sample_note_results, "revolution", "text")
        
        # Should print a table
        assert mock_console.print.called
        call_args = mock_console.print.call_args
        printed_obj = call_args[0][0]
        assert not isinstance(printed_obj, str) or "No notes found" not in printed_obj
    
    @patch('src.commands.search.console')
    def test_display_note_results_shows_no_results_message(self, mock_console):
        """Test that display_note_results shows message when no results."""
        display_note_results_tree([], "nonexistent", "all")
        
        # Should print "No notes found" message
        assert mock_console.print.called
        call_args = mock_console.print.call_args[0][0]
        assert "No notes found" in call_args
        assert "nonexistent" in call_args


