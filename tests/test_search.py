"""Tests for search functionality."""

import pytest
from src.models.address_book import AddressBook
from src.models.record import Record
from src.services.search_service import SearchService, ContactSearchType, NoteSearchType


@pytest.fixture
def search_service():
    """Create a contact service with test data for searching."""
    book = AddressBook()
    
    # Add contacts with various data
    john = Record("John Doe")
    john.add_phone("1234567890")
    john.add_tag("work")
    john.add_tag("important")
    john.add_note("Meeting", "Discuss Q4 targets with the team")
    john.add_note("Todo", "Follow up on email")
    john.note_add_tag("Meeting", "urgent")
    john.note_add_tag("Meeting", "work")
    book.add_record(john)
    
    alice = Record("Alice Smith")
    alice.add_phone("0987654321")
    alice.add_tag("personal")
    alice.add_note("Ideas", "New project ideas for next quarter")
    alice.note_add_tag("Ideas", "creative")
    book.add_record(alice)
    
    bob = Record("Bob Johnson")
    bob.add_phone("5551234567")
    bob.add_tag("work")
    bob.add_note("Meeting", "Team sync notes")
    book.add_record(bob)
    
    return SearchService(book)


class TestSearchServiceUtilities:
    """Tests for search service utility methods."""
    
    def test_has_contacts_with_data(self, search_service):
        """Test has_contacts returns True when contacts exist."""
        assert search_service.has_contacts() is True
    
    def test_has_contacts_empty(self):
        """Test has_contacts returns False when empty."""
        empty_service = SearchService(AddressBook())
        assert empty_service.has_contacts() is False
    
    def test_list_contacts(self, search_service):
        """Test list_contacts returns sorted contacts with phones."""
        contacts = search_service.list_contacts()
        assert len(contacts) == 3
        # Should be sorted alphabetically
        assert contacts[0][0] == "Alice Smith"
        assert contacts[1][0] == "Bob Johnson"
        assert contacts[2][0] == "John Doe"
        # Check phones are included
        assert "0987654321" in contacts[0][1]
    
    def test_list_contacts_no_phone(self):
        """Test list_contacts handles contacts without phones."""
        book = AddressBook()
        record = Record("NoPhone")
        book.add_record(record)
        service = SearchService(book)
        
        contacts = service.list_contacts()
        assert len(contacts) == 1
        assert contacts[0] == ("NoPhone", "No phone")


class TestContactSearch:
    """Tests for contact search functionality."""
    
    def test_search_contacts_by_all_finds_by_name(self, search_service):
        """Test searching all fields finds by name."""
        results = search_service.search_contacts("john doe", ContactSearchType.ALL)
        assert len(results) == 1
        assert results[0][0] == "John Doe"
    
    def test_search_contacts_by_all_finds_by_phone(self, search_service):
        """Test searching all fields finds by phone."""
        results = search_service.search_contacts("1234567890", ContactSearchType.ALL)
        assert len(results) == 1
        assert results[0][0] == "John Doe"
    
    def test_search_contacts_by_all_finds_by_tag(self, search_service):
        """Test searching all fields finds by tag."""
        results = search_service.search_contacts("work", ContactSearchType.ALL)
        assert len(results) == 2
        names = [name for name, _ in results]
        assert "John Doe" in names
        assert "Bob Johnson" in names
    
    def test_search_contacts_by_all_finds_by_note_text(self, search_service):
        """Test searching all fields finds by note content."""
        results = search_service.search_contacts("targets", ContactSearchType.ALL)
        assert len(results) == 1
        assert results[0][0] == "John Doe"
    
    def test_search_contacts_by_all_finds_by_note_name(self, search_service):
        """Test searching all fields finds by note name."""
        results = search_service.search_contacts("meeting", ContactSearchType.ALL)
        assert len(results) == 2
        names = [name for name, _ in results]
        assert "John Doe" in names
        assert "Bob Johnson" in names
    
    def test_search_contacts_by_all_finds_by_note_tags(self, search_service):
        """Test searching all fields finds by note tags."""
        results = search_service.search_contacts("urgent", ContactSearchType.ALL)
        assert len(results) == 1
        assert results[0][0] == "John Doe"
    
    def test_search_contacts_by_name_only(self, search_service):
        """Test searching by name field only."""
        results = search_service.search_contacts("alice", ContactSearchType.NAME)
        assert len(results) == 1
        assert results[0][0] == "Alice Smith"
    
    def test_search_contacts_by_name_case_insensitive(self, search_service):
        """Test name search is case insensitive."""
        results = search_service.search_contacts("ALICE", ContactSearchType.NAME)
        assert len(results) == 1
        assert results[0][0] == "Alice Smith"
    
    def test_search_contacts_by_phone_only(self, search_service):
        """Test searching by phone field only."""
        results = search_service.search_contacts("0987", ContactSearchType.PHONE)
        assert len(results) == 1
        assert results[0][0] == "Alice Smith"
    
    def test_search_contacts_by_tags_only(self, search_service):
        """Test searching by tags field only."""
        results = search_service.search_contacts("personal", ContactSearchType.TAGS)
        assert len(results) == 1
        assert results[0][0] == "Alice Smith"
    
    def test_search_contacts_by_notes_text_only(self, search_service):
        """Test searching by note content only."""
        results = search_service.search_contacts("project", ContactSearchType.NOTES_TEXT)
        assert len(results) == 1
        assert results[0][0] == "Alice Smith"
    
    def test_search_contacts_by_notes_name_only(self, search_service):
        """Test searching by note name only."""
        results = search_service.search_contacts("todo", ContactSearchType.NOTES_NAME)
        assert len(results) == 1
        assert results[0][0] == "John Doe"
    
    def test_search_contacts_by_notes_tags_only(self, search_service):
        """Test searching by note tags only."""
        results = search_service.search_contacts("creative", ContactSearchType.NOTES_TAGS)
        assert len(results) == 1
        assert results[0][0] == "Alice Smith"
    
    def test_search_contacts_no_results(self, search_service):
        """Test search returns empty list when no matches."""
        results = search_service.search_contacts("nonexistent", ContactSearchType.ALL)
        assert results == []
    
    def test_search_contacts_by_tags_all_with_multiple_tags(self, search_service):
        """Test searching for contacts with ALL specified tags (AND logic)."""
        results = search_service.search_contacts("work,important", ContactSearchType.TAGS_ALL)
        assert len(results) == 1
        assert results[0][0] == "John Doe"  # Has both 'work' and 'important' tags
    
    def test_search_contacts_by_tags_all_no_match(self, search_service):
        """Test TAGS_ALL returns empty when no contact has all tags."""
        results = search_service.search_contacts("work,personal", ContactSearchType.TAGS_ALL)
        assert results == []  # No contact has both 'work' and 'personal'
    
    def test_search_contacts_by_tags_any_with_multiple_tags(self, search_service):
        """Test searching for contacts with ANY specified tag (OR logic)."""
        results = search_service.search_contacts("work,personal", ContactSearchType.TAGS_ANY)
        assert len(results) == 3  # John (work), Alice (personal), Bob (work)
        names = [name for name, _ in results]
        assert "John Doe" in names
        assert "Alice Smith" in names
        assert "Bob Johnson" in names
    
    def test_search_contacts_by_tags_any_single_match(self, search_service):
        """Test TAGS_ANY with only one contact matching."""
        results = search_service.search_contacts("personal", ContactSearchType.TAGS_ANY)
        assert len(results) == 1
        assert results[0][0] == "Alice Smith"
    
    def test_search_contacts_partial_match(self, search_service):
        """Test search works with partial matches."""
        results = search_service.search_contacts("doe", ContactSearchType.NAME)
        assert len(results) == 1
        assert results[0][0] == "John Doe"


class TestNoteSearch:
    """Tests for note search functionality."""
    
    def test_search_notes_by_all_finds_by_name(self, search_service):
        """Test searching all fields finds by note name."""
        results = search_service.search_notes("meeting", NoteSearchType.ALL)
        assert len(results) == 2
        contact_names = [contact_name for contact_name, _, _ in results]
        assert "John Doe" in contact_names
        assert "Bob Johnson" in contact_names
    
    def test_search_notes_by_all_finds_by_text(self, search_service):
        """Test searching all fields finds by note content."""
        results = search_service.search_notes("targets", NoteSearchType.ALL)
        assert len(results) == 1
        assert results[0][0] == "John Doe"
        assert results[0][1] == "Meeting"
    
    def test_search_notes_by_all_finds_by_tags(self, search_service):
        """Test searching all fields finds by note tags."""
        results = search_service.search_notes("creative", NoteSearchType.ALL)
        assert len(results) == 1
        assert results[0][0] == "Alice Smith"
        assert results[0][1] == "Ideas"
    
    def test_search_notes_by_all_finds_by_contact_name(self, search_service):
        """Test searching all fields finds by contact name."""
        results = search_service.search_notes("alice", NoteSearchType.ALL)
        assert len(results) == 1
        assert results[0][0] == "Alice Smith"
    
    def test_search_notes_by_all_finds_by_contact_phone(self, search_service):
        """Test searching all fields finds by contact phone."""
        results = search_service.search_notes("1234567890", NoteSearchType.ALL)
        assert len(results) == 2
        note_names = [note_name for _, note_name, _ in results]
        assert "Meeting" in note_names
        assert "Todo" in note_names
    
    def test_search_notes_by_name_only(self, search_service):
        """Test searching by note name field only."""
        results = search_service.search_notes("ideas", NoteSearchType.NAME)
        assert len(results) == 1
        assert results[0][0] == "Alice Smith"
        assert results[0][1] == "Ideas"
    
    def test_search_notes_by_text_only(self, search_service):
        """Test searching by note content field only."""
        results = search_service.search_notes("quarter", NoteSearchType.TEXT)
        assert len(results) == 1
        assert results[0][0] == "Alice Smith"
    
    def test_search_notes_by_tags_only(self, search_service):
        """Test searching by note tags field only."""
        results = search_service.search_notes("urgent", NoteSearchType.TAGS)
        assert len(results) == 1
        assert results[0][0] == "John Doe"
        assert results[0][1] == "Meeting"
    
    def test_search_notes_by_contact_name_only(self, search_service):
        """Test searching by contact name field only."""
        results = search_service.search_notes("bob", NoteSearchType.CONTACT_NAME)
        assert len(results) == 1
        assert results[0][0] == "Bob Johnson"
    
    def test_search_notes_by_contact_phone_only(self, search_service):
        """Test searching by contact phone field only."""
        results = search_service.search_notes("555", NoteSearchType.CONTACT_PHONE)
        assert len(results) == 1
        assert results[0][0] == "Bob Johnson"
    
    def test_search_notes_by_contact_tags_only(self, search_service):
        """Test searching by contact tags field only."""
        results = search_service.search_notes("personal", NoteSearchType.CONTACT_TAGS)
        assert len(results) == 1
        assert results[0][0] == "Alice Smith"
    
    def test_search_notes_no_results(self, search_service):
        """Test search returns empty list when no matches."""
        results = search_service.search_notes("nonexistent", NoteSearchType.ALL)
        assert results == []
    
    def test_search_notes_case_insensitive(self, search_service):
        """Test note search is case insensitive."""
        results = search_service.search_notes("IDEAS", NoteSearchType.NAME)
        assert len(results) == 1
        assert results[0][0] == "Alice Smith"
    
    def test_search_notes_partial_match(self, search_service):
        """Test note search works with partial matches."""
        results = search_service.search_notes("sync", NoteSearchType.TEXT)
        assert len(results) == 1
        assert results[0][0] == "Bob Johnson"


class TestSearchEdgeCases:
    """Tests for search edge cases."""
    
    def test_search_contacts_empty_query(self, search_service):
        """Test search with empty query returns all contacts."""
        results = search_service.search_contacts("", ContactSearchType.ALL)
        assert len(results) == 3
    
    def test_search_notes_empty_query(self, search_service):
        """Test search with empty query returns all notes."""
        results = search_service.search_notes("", NoteSearchType.ALL)
        assert len(results) == 4
    
    def test_search_contacts_special_characters(self, search_service):
        """Test search handles special characters."""
        results = search_service.search_contacts("@", ContactSearchType.ALL)
        assert results == []
    
    def test_search_notes_returns_tuples(self, search_service):
        """Test search notes returns proper tuple structure."""
        results = search_service.search_notes("meeting", NoteSearchType.NAME)
        for result in results:
            assert isinstance(result, tuple)
            assert len(result) == 3
            contact_name, note_name, note = result
            assert isinstance(contact_name, str)
            assert isinstance(note_name, str)
            assert hasattr(note, 'content')

