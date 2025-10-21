"""Contact record class for storing contact information."""

from typing import Optional
from src.models.name import Name
from src.models.phone import Phone
from src.models.birthday import Birthday


class Record:
    """
    Class for storing contact information including name, phones, and birthday.
    
    Attributes:
        name: Contact's name (Name object)
        phones: List of phone numbers (Phone objects)
        birthday: Contact's birthday (Birthday object, optional)
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize a contact record with a name.
        
        Args:
            name: The contact's name
        """
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.birthday: Optional[Birthday] = None
    
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
        for phone_obj in self.phones:
            if phone_obj.value == phone:
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
    
    def __str__(self) -> str:
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"
    
    def __repr__(self) -> str:
        return f"Record(name={self.name.value!r}, phones={[p.value for p in self.phones]})"

