"""Address book class for managing contact records."""

import pickle
from collections import UserDict
from pathlib import Path
from typing import Optional
from typing import Iterable
from src.models.record import Record
from src.models.group import Group, DEFAULT_GROUP_ID, normalize_group_id


class AddressBook(UserDict):
    """
    Class for storing and managing contact records.
    
    Inherits from UserDict to provide dictionary-like interface.
    Records are stored with contact name as key.
    
    Attributes:
        data: Dictionary storing contact records (inherited from UserDict)
    """
    
    # unique key for record
    def _make_key(self, name: str, group_id: str) -> str:
        gid = group_id or self.current_group_id
        return f"{gid}:{name}"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # id -> Group
        self.groups: dict[str, Group] = {}
        # ensure default group exists
        if DEFAULT_GROUP_ID not in self.groups:
            self.groups[DEFAULT_GROUP_ID] = Group(DEFAULT_GROUP_ID, DEFAULT_GROUP_ID)
        self.current_group_id: str = DEFAULT_GROUP_ID
    
    def add_record(self, record: Record) -> None:
        """
        Add a contact record to the address book.
        
        Args:
            record: The Record object to add
            
        Raises:
            ValueError: If record with this name already exists
        """
        gid = record.group_id or self.current_group_id
        key = self._make_key(record.name.value, gid)
        if key in self.data:
            raise ValueError(
                f"Record with name {record.name.value} already exists in group {gid}."
            )
        self.data[key] = record
    
    def find(self, name: str, group_id: str | None = None) -> Optional[Record]:
        """
        Find a contact record by name.y)
        
        Args:
            name: The contact name to search for
            
        Returns:
            Record object if found, None otherwise
        """
        key = self._make_key(name, group_id or self.current_group_id)
        return self.data.get(key)
    
    def delete(self, name: str, group_id: str | None = None) -> None:
        """
        Delete a contact record by name.
        
        Args:
            name: The contact name to delete
            
        Raises:
            KeyError: If record with this name is not found
        """
        key = self._make_key(name, group_id)
        if key not in self.data:
            raise KeyError(f"Record with name {name} not found")
        del self.data[key]
        
    def __str__(self) -> str:
        if not self.data:
            return "Address book is empty"
        
        contacts = [str(record) for record in self.data.values()]
        return "\n".join(contacts)
    
    def __repr__(self) -> str:
        return f"AddressBook(records={len(self.data)})"
    
    def save_to_file(self, filename: str = "addressbook.pkl") -> None:
        """
        Save address book to file using pickle serialization.
        
        Model is responsible for its own persistence (serialization).
        
        Args:
            filename: Path to the file where data will be saved
            
        Raises:
            ValueError: If file cannot be saved (permissions, disk space, etc.)
        """
        filepath = Path(filename)
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "wb") as f:
                pickle.dump(self, f)
        except (IOError, OSError) as e:
            raise ValueError(f"Failed to save address book: {str(e)}")
    
    @classmethod
    def load_from_file(cls, filename: str = "addressbook.pkl") -> "AddressBook":
        """
        Load address book from file using pickle deserialization.
        
        Model is responsible for its own persistence (deserialization).
        
        Args:
            filename: Path to the file to load data from
            
        Returns:
            AddressBook instance loaded from file, or new empty AddressBook
            if file not found
            
        Raises:
            ValueError: If file exists but cannot be loaded (corrupted, wrong format, etc.)
        """
        filepath = Path(filename)
        try:
            with open(filepath, "rb") as f:
                book: AddressBook = pickle.load(f)
        except FileNotFoundError:
            return cls()
        except (IOError, OSError, pickle.UnpicklingError) as e:
            raise ValueError(f"Failed to load address book: {str(e)}")

        # migrate groups container
        if not hasattr(book, "groups") or not isinstance(book.groups, dict):
            book.groups = {DEFAULT_GROUP_ID: Group(DEFAULT_GROUP_ID)}

        # migrate records' group_id
        for rec in book.data.values():
            if not hasattr(rec, "group_id") or not rec.group_id:
                rec.group_id = DEFAULT_GROUP_ID
            # ensure group exists
            gid = normalize_group_id(rec.group_id)
            rec.group_id = gid
            if gid not in book.groups:
                book.groups[gid] = Group(gid)

        return book
    
    # --- Groups API ---
    def add_group(self, group_id: str, title: str | None = None) -> Group:
        gid = normalize_group_id(group_id)
        if gid in self.groups:
            raise ValueError(f"Group '{gid}' already exists.")
        group = Group(gid, title)
        self.groups[gid] = group
        return group

    def has_group(self, group_id: str) -> bool:
        gid = normalize_group_id(group_id)
        return gid in self.groups

    def iter_groups(self) -> Iterable[Group]:
        """Iterate over all groups."""
        return self.groups.values()

    def iter_group(self, group_id: str) -> list[tuple[str, "Record"]]:
        """Contacts only from given group."""
        gid = normalize_group_id(group_id)
        prefix = f"{gid}:"
        result: list[tuple[str, "Record"]] = []
        for key, rec in self.data.items():
            if key.startswith(prefix):
                name = key[len(prefix):]
                result.append((name, rec))
        return result

    def iter_all(self) -> list[tuple[str, "Record"]]:
        """Contacts from all groups."""
        result: list[tuple[str, "Record"]] = []
        for key, rec in self.data.items():
            _, name = key.split(":", 1)
            result.append((name, rec))
        return result
