"""Address book class for managing contact records."""

import pickle
from collections import UserDict
from pathlib import Path
from typing import Optional
from src.models.record import Record


class AddressBook(UserDict):
    """
    Class for storing and managing contact records.
    
    Inherits from UserDict to provide dictionary-like interface.
    Records are stored with contact name as key.
    
    Attributes:
        data: Dictionary storing contact records (inherited from UserDict)
    """
    
    def add_record(self, record: Record) -> None:
        """
        Add a contact record to the address book.
        
        Args:
            record: The Record object to add
            
        Raises:
            ValueError: If record with this name already exists
        """
        if record.name.value in self.data:
            raise ValueError(f"Record with name {record.name.value} already exists")
        self.data[record.name.value] = record
    
    def find(self, name: str) -> Optional[Record]:
        """
        Find a contact record by name.
        
        Args:
            name: The contact name to search for
            
        Returns:
            Record object if found, None otherwise
        """
        return self.data.get(name)
    
    def delete(self, name: str) -> None:
        """
        Delete a contact record by name.
        
        Args:
            name: The contact name to delete
            
        Raises:
            KeyError: If record with this name is not found
        """
        if name not in self.data:
            raise KeyError(f"Record with name {name} not found")
        del self.data[name]
    
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
                return pickle.load(f)
        except FileNotFoundError:
            return cls()
        except (IOError, OSError, pickle.UnpicklingError) as e:
            raise ValueError(f"Failed to load address book: {str(e)}")

