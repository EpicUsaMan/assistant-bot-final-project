"""Contact record class for storing contact information."""

from typing import Optional

from src.models.birthday import Birthday
from src.models.name import Name
from src.models.note import Note
from src.models.phone import Phone
from src.models.email import Email
from src.models.address import Address
from src.models.tags import Tags
from src.utils.validators import is_valid_tag, normalize_tag

from src.models.group import DEFAULT_GROUP_ID


class Record:
    """
    Class for storing contact information including name, phones, birthday, email, address, and notes.
    
    Attributes:
        name: Contact's name (Name object)
        phones: List of phone numbers (Phone objects)
        birthday: Contact's birthday (Birthday object, optional)
        email: Contact's email (Email object, optional)
        address: Contact's address (Address object, optional)
        tags: Contact's tags (Tags object)
        notes: Dictionary of notes (Note objects, keyed by note name)
    """
    
    def __init__(self, name: str, group_id: str | None = None) -> None:
        """
        Initialize a contact record with a name.
        
        Args:
            name: The contact's name
            group_id: Group identifier (optional)
        """
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.birthday: Optional[Birthday] = None
        self.email: Optional[Email] = None
        self.address: Optional[Address] = None
        self.tags = Tags()
        self.notes: dict[str, Note] = {}
        self.group_id: str | None = group_id

    def add_phone(self, phone: str) -> None:
        """
        Add a phone number to the contact.
        
        Args:
            phone: The phone number to add (must be 10 digits)
            
        Raises:
            ValueError: If phone number format is invalid
        """
        phone_obj = Phone(phone)
        if phone_obj in self.phones:
            raise ValueError(f"Phone {phone} already exists for this contact")
        self.phones.append(phone_obj)
    
    def remove_phone(self, phone: str) -> None:
        """
        Remove a phone number from the contact.
        
        Args:
            phone: The phone number to remove
            
        Raises:
            ValueError: If phone number is not found
        """
        phone_obj = self.find_phone(phone)
        if phone_obj is None:
            raise ValueError(f"Phone {phone} not found")
        self.phones.remove(phone_obj)
    
    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        """
        Edit an existing phone number.
        
        Args:
            old_phone: The phone number to replace
            new_phone: The new phone number (must be 10 digits)
            
        Raises:
            ValueError: If old phone is not found or new phone format is invalid
        """
        phone_obj = self.find_phone(old_phone)
        if phone_obj is None:
            raise ValueError(f"Phone {old_phone} not found")
        
        new_phone_obj = Phone(new_phone)
        phone_index = self.phones.index(phone_obj)
        self.phones[phone_index] = new_phone_obj
    
    def find_phone(self, phone: str) -> Optional[Phone]:
        """
        Find a phone number in the contact.
        
        Args:
            phone: The phone number to find
            
        Returns:
            Phone object if found, None otherwise
        """
        canonical = Phone(phone).value
        for phone_obj in self.phones:
            if phone_obj.value == canonical:
                return phone_obj
        return None
    
    def add_birthday(self, birthday: str) -> None:
        """
        Add a birthday to the contact.
        
        Args:
            birthday: The birthday date in DD.MM.YYYY format
            
        Raises:
            ValueError: If birthday format is invalid
        """
        self.birthday = Birthday(birthday)
    
    def add_email(self, email: str) -> None:
        """
        Add or update email address for the contact.
        
        Args:
            email: The email address
            
        Raises:
            ValueError: If email format is invalid
        """
        self.email = Email(email)
    
    def remove_email(self) -> None:
        """Remove email address from the contact."""
        self.email = None
    
    def set_address(
        self,
        country: str,
        city: str,
        address_line: str,
    ) -> None:
        """
        Set address for the contact.
        
        Args:
            country: Country code (e.g., "UA", "PL")
            city: City name
            address_line: Street address
        """
        self.address = Address(country, city, address_line)
    
    def remove_address(self) -> None:
        """Remove address information from the contact."""
        self.address = None
    
    def __str__(self) -> str:
        phones_str = '; '.join(p.display_value for p in self.phones) if self.phones else ""
        parts = [f"Contact name: {self.name.value}"]
        
        if phones_str:
            parts.append(f"phones: {phones_str}")
        if self.birthday:
            parts.append(f"birthday: {self.birthday}")
        if self.email:
            parts.append(f"email: {self.email.value}")
        if self.address and not self.address.is_empty():
            parts.append(f"address: {self.address}")
        
        return ", ".join(parts)
    
    def __repr__(self) -> str:
        return f"Record(name={self.name.value!r}, phones={[p.value for p in self.phones]})"

    def __getstate__(self) -> dict:
        return self.__dict__

    def __setstate__(self, state: dict) -> None:
        """Backward compatibility for old pickles (no tags / no group_id / no email / no address)."""
        self.__dict__.update(state)

        if "tags" not in self.__dict__:
            self.tags = Tags()
        
        # migrate phone instances / raw strings
        migrated: list[Phone] = []
        for item in getattr(self, "phones", []):
            if isinstance(item, Phone):
                # recreate phone object from canonical string
                migrated.append(Phone(item.display_value))
            else:
                # in case a string was saved in the pickle
                migrated.append(Phone(str(item)))
        self.phones = migrated

        if not hasattr(self, "group_id") or not self.group_id:
            self.group_id = DEFAULT_GROUP_ID
        
        # Initialize new fields if missing
        if "email" not in self.__dict__:
            self.email = None
        if "address" not in self.__dict__:
            self.address = None
        # Handle old format where address was stored as separate fields
        elif not isinstance(self.address, Address):
            # If address is not an Address object, try to migrate from old format
            if hasattr(self, "country") or hasattr(self, "city") or hasattr(self, "address_line"):
                country = getattr(self, "country", None)
                city = getattr(self, "city", None)
                address_line = getattr(self, "address_line", None)
                if country or city or address_line:
                    self.address = Address(
                        country or "",
                        city or "",
                        address_line or ""
                    )
                else:
                    self.address = None
                # Clean up old fields
                if hasattr(self, "country"):
                    delattr(self, "country")
                if hasattr(self, "city"):
                    delattr(self, "city")
                if hasattr(self, "address_line"):
                    delattr(self, "address_line")
            else:
                self.address = None

    # --- Tags API ---
    def set_tags(self, tags: list[str] | str):
        """
        Replace all tags at once. Accepts list or comma-separated string.
        Args:
            tags: List of tags or comma-separated string of tags
        """
        if isinstance(tags, str):
            from src.utils.validators import split_tags_string

            tags = split_tags_string(tags)
        self.tags.replace(tags)

    def add_tag(self, tag: str) -> None:
        """
        Add a single tag.
        Args:
            tag: Tag to add
        Raises:
            ValueError: If tag format is invalid
        """
        n = normalize_tag(tag)
        if not is_valid_tag(n):
            raise ValueError(f"Invalid tag: '{tag}'")
        self.tags.add(n)

    def remove_tag(self, tag: str) -> None:
        """
        Remove a single tag.
        Args:
            tag: Tag to remove
        """
        n = normalize_tag(tag)
        self.tags.remove(n)

    def clear_tags(self) -> None:
        """
        Clear all tags.
        """
        self.tags.clear()

    def tags_list(self) -> list[str]:
        return self.tags.as_list()

    def has_tags_all(self, tags: list[str]) -> bool:
        """
        Return True if note has *all* of tags (AND).
        """
        return all(t in self.tags.as_list() for t in tags)

    def has_tags_any(self, tags: list[str]) -> bool:
        """
        Return True if note has *any* of tags (OR).
        """
        return any(t in self.tags.as_list() for t in tags)

    # --- Notes API ---
    def add_note(self, name: str, content: str = "") -> None:
        """
        Add a note to the contact.
        
        Args:
            name: Note name/title (acts as unique identifier)
            content: Note text content (default: empty string)
            
        Raises:
            ValueError: If note with this name already exists or name is empty
        """
        if name in self.notes:
            raise ValueError(f"Note '{name}' already exists for this contact")
        
        note = Note(name, content)
        self.notes[name] = note
    
    def find_note(self, name: str) -> Optional[Note]:
        """
        Find a note by name.
        
        Args:
            name: Note name to find
            
        Returns:
            Note object if found, None otherwise
        """
        return self.notes.get(name)
    
    def edit_note(self, name: str, content: str) -> None:
        """
        Edit an existing note's content.
        
        Args:
            name: Note name
            content: New text content
            
        Raises:
            ValueError: If note is not found
        """
        note = self.find_note(name)
        if note is None:
            raise ValueError(f"Note '{name}' not found")
        note.update_content(content)
    
    def delete_note(self, name: str) -> None:
        """
        Delete a note from the contact.
        
        Args:
            name: Note name to delete
            
        Raises:
            ValueError: If note is not found
        """
        if name not in self.notes:
            raise ValueError(f"Note '{name}' not found")
        del self.notes[name]
    
    def list_notes(self) -> list[Note]:
        """
        Get list of all notes.
        
        Returns:
            List of Note objects
        """
        return list(self.notes.values())
    
    def note_add_tag(self, note_name: str, tag: str) -> None:
        """
        Add a tag to a specific note.
        
        Args:
            note_name: Name of the note
            tag: Tag to add
            
        Raises:
            ValueError: If note not found or tag format is invalid
        """
        note = self.find_note(note_name)
        if note is None:
            raise ValueError(f"Note '{note_name}' not found")
        note.add_tag(tag)
    
    def note_remove_tag(self, note_name: str, tag: str) -> None:
        """
        Remove a tag from a specific note.
        
        Args:
            note_name: Name of the note
            tag: Tag to remove
            
        Raises:
            ValueError: If note not found
        """
        note = self.find_note(note_name)
        if note is None:
            raise ValueError(f"Note '{note_name}' not found")
        note.remove_tag(tag)
    
    def note_clear_tags(self, note_name: str) -> None:
        """
        Clear all tags from a specific note.
        
        Args:
            note_name: Name of the note
            
        Raises:
            ValueError: If note not found
        """
        note = self.find_note(note_name)
        if note is None:
            raise ValueError(f"Note '{note_name}' not found")
        note.clear_tags()
    
    def note_list_tags(self, note_name: str) -> list[str]:
        """
        Get list of all tags for a specific note.
        
        Args:
            note_name: Name of the note
            
        Returns:
            List of tag strings
            
        Raises:
            ValueError: If note not found
        """
        note = self.find_note(note_name)
        if note is None:
            raise ValueError(f"Note '{note_name}' not found")
        return note.tags_list()
