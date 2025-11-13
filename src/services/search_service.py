"""
Search service for advanced search operations on contacts and notes.

This service provides business logic for searching through contacts
and notes with various search criteria and filters.
"""

from enum import Enum
from typing import List, Tuple

from src.models.address_book import AddressBook
from src.models.note import Note
from src.models.record import Record
from src.models.group import DEFAULT_GROUP_ID


class ContactSearchType(str, Enum):
    """
    Enum for contact search criteria.
    
    Attributes:
        ALL: Search across all contact fields
        NAME: Search by contact name
        PHONE: Search by phone number
        TAGS: Search by contact tags (substring match)
        TAGS_ALL: Search contacts with ALL specified tags (exact match, AND logic)
        TAGS_ANY: Search contacts with ANY specified tag (exact match, OR logic)
        NOTES_TEXT: Search in note content
        NOTES_NAME: Search by note titles
        NOTES_TAGS: Search by note tags
    """
    ALL = "all"
    NAME = "name"
    PHONE = "phone"
    TAGS = "tags"
    TAGS_ALL = "tags-all"
    TAGS_ANY = "tags-any"
    NOTES_TEXT = "notes-text"
    NOTES_NAME = "notes-name"
    NOTES_TAGS = "notes-tags"


class NoteSearchType(str, Enum):
    """
    Enum for note search criteria.
    
    Attributes:
        ALL: Search across all note fields
        NAME: Search by note name/title
        TEXT: Search in note content
        TAGS: Search by note tags
        CONTACT_NAME: Find notes by contact name
        CONTACT_PHONE: Find notes by contact phone
        CONTACT_TAGS: Find notes by contact tags
    """
    ALL = "all"
    NAME = "name"
    TEXT = "text"
    TAGS = "tags"
    CONTACT_NAME = "contact-name"
    CONTACT_PHONE = "contact-phone"
    CONTACT_TAGS = "contact-tags"


class SearchService:
    """
    Service for advanced search operations.
    
    This class encapsulates all business logic for searching through
    contacts and notes with various search criteria and filters.
    """
    
    def __init__(self, address_book: AddressBook):
        """
        Initialize the search service.
        
        Args:
            address_book: The address book instance to search in
        """
        self.address_book = address_book
    
    @property
    def current_group_id(self) -> str:
        """Get the current active group id from AddressBook."""
        return getattr(self.address_book, "current_group_id", DEFAULT_GROUP_ID)
    
    def has_contacts(self) -> bool:
        """
        Check if there are any contacts in the address book.
        
        Returns:
            True if there are contacts, False otherwise
        """
        return len(self.address_book.data) > 0
    
    def list_contacts(self) -> list[tuple[str, str]]:
        """
        List contacts in current group with their phone numbers.
        
        Returns:
            List of tuples (contact_name, phones_str) from current group
        """
        result = []
        current_group = self.current_group_id
        
        for key, record in self.address_book.data.items():
            # Filter by current group
            if ":" in key:
                group_id, name = key.split(":", 1)
                if group_id != current_group:
                    continue
            else:
                name = key
            
            phones_str = ", ".join(p.value for p in record.phones) if record.phones else "No phone"
            result.append((name, phones_str))
        return sorted(result, key=lambda x: x[0])
    
    def search_contacts(
        self, query: str, search_type: ContactSearchType = ContactSearchType.ALL
    ) -> List[Tuple[str, Record]]:
        """
        Search contacts in current group by various criteria.
        
        Args:
            query: Search query string (for tags-all and tags-any, use comma-separated tags)
            search_type: Type of search to perform (default: ALL)
            
        Returns:
            List of (contact_name, Record) tuples matching the search in current group
            
        Examples:
            search_contacts("john", ContactSearchType.NAME)
            search_contacts("work,important", ContactSearchType.TAGS_ALL)  # Must have both tags
            search_contacts("work,personal", ContactSearchType.TAGS_ANY)   # Must have at least one
        """
        results: List[Tuple[str, Record]] = []
        query_lower = query.lower()
        current_group = self.current_group_id
        
        # Handle multi-tag searches
        if search_type in (ContactSearchType.TAGS_ALL, ContactSearchType.TAGS_ANY):
            # Split by comma and normalize
            search_tags = [tag.strip().lower() for tag in query.split(',') if tag.strip()]
            
            for key, record in self.address_book.data.items():
                # Filter by current group
                if ":" in key:
                    group_id, name = key.split(":", 1)
                    if group_id != current_group:
                        continue
                else:
                    name = key
                    
                contact_tags = [tag.lower() for tag in record.tags_list()]
                
                if search_type == ContactSearchType.TAGS_ALL:
                    # ALL tags must be present (AND logic)
                    if all(tag in contact_tags for tag in search_tags):
                        results.append((name, record))
                elif search_type == ContactSearchType.TAGS_ANY:
                    # ANY tag must be present (OR logic)
                    if any(tag in contact_tags for tag in search_tags):
                        results.append((name, record))
            
            return results
        
        # Regular searches
        for key, record in self.address_book.data.items():
            # Filter by current group
            if ":" in key:
                group_id, name = key.split(":", 1)
                if group_id != current_group:
                    continue
            else:
                name = key
            
            match = False
            
            if search_type == ContactSearchType.ALL:
                # Search across all fields
                if (query_lower in name.lower() or
                    any(query_lower in phone.value for phone in record.phones) or
                    any(query_lower in tag for tag in record.tags_list()) or
                    any(query_lower in note.content.lower() for note in record.list_notes()) or
                    any(query_lower in note.name.lower() for note in record.list_notes()) or
                    any(query_lower in tag for note in record.list_notes() for tag in note.tags_list())):
                    match = True
            
            elif search_type == ContactSearchType.NAME:
                if query_lower in name.lower():
                    match = True
            
            elif search_type == ContactSearchType.PHONE:
                if any(query_lower in phone.value for phone in record.phones):
                    match = True
            
            elif search_type == ContactSearchType.TAGS:
                if any(query_lower in tag for tag in record.tags_list()):
                    match = True
            
            elif search_type == ContactSearchType.NOTES_TEXT:
                if any(query_lower in note.content.lower() for note in record.list_notes()):
                    match = True
            
            elif search_type == ContactSearchType.NOTES_NAME:
                if any(query_lower in note.name.lower() for note in record.list_notes()):
                    match = True
            
            elif search_type == ContactSearchType.NOTES_TAGS:
                if any(query_lower in tag for note in record.list_notes() for tag in note.tags_list()):
                    match = True
            
            if match:
                results.append((name, record))
        
        return results
    
    def search_notes(
        self, query: str, search_type: NoteSearchType = NoteSearchType.ALL
    ) -> List[Tuple[str, str, Note]]:
        """
        Search notes in current group by various criteria.
        
        Args:
            query: Search query string
            search_type: Type of search to perform (default: ALL)
            
        Returns:
            List of (contact_name, note_name, Note) tuples matching the search in current group
        """
        results: List[Tuple[str, str, Note]] = []
        query_lower = query.lower()
        current_group = self.current_group_id
        
        for key, record in self.address_book.data.items():
            # Filter by current group
            if ":" in key:
                group_id, contact_name = key.split(":", 1)
                if group_id != current_group:
                    continue
            else:
                contact_name = key
            
            for note in record.list_notes():
                match = False
                
                if search_type == NoteSearchType.ALL:
                    # Search across all note and contact fields
                    if (query_lower in note.name.lower() or
                        query_lower in note.content.lower() or
                        any(query_lower in tag for tag in note.tags_list()) or
                        query_lower in contact_name.lower() or
                        any(query_lower in phone.value for phone in record.phones) or
                        any(query_lower in tag for tag in record.tags_list())):
                        match = True
                
                elif search_type == NoteSearchType.NAME:
                    if query_lower in note.name.lower():
                        match = True
                
                elif search_type == NoteSearchType.TEXT:
                    if query_lower in note.content.lower():
                        match = True
                
                elif search_type == NoteSearchType.TAGS:
                    if any(query_lower in tag for tag in note.tags_list()):
                        match = True
                
                elif search_type == NoteSearchType.CONTACT_NAME:
                    if query_lower in contact_name.lower():
                        match = True
                
                elif search_type == NoteSearchType.CONTACT_PHONE:
                    if any(query_lower in phone.value for phone in record.phones):
                        match = True
                
                elif search_type == NoteSearchType.CONTACT_TAGS:
                    if any(query_lower in tag for tag in record.tags_list()):
                        match = True
                
                if match:
                    results.append((contact_name, note.name, note))
        
        return results



