"""
Contact service for managing contacts in the address book.

This service provides business logic for contact operations with proper
separation of concerns and dependency injection support.
"""

from typing import Optional, List, Dict
from datetime import datetime, timedelta
from src.models.address_book import AddressBook
from src.models.record import Record


class ContactService:
    """
    Service for managing contacts in an address book.
    
    This class encapsulates all business logic for contact operations,
    making it easy to test and inject dependencies.
    """
    
    def __init__(self, address_book: AddressBook) -> None:
        """
        Initialize the contact service.
        
        Args:
            address_book: The address book instance to manage
        """
        self.address_book = address_book
    
    def add_contact(self, name: str, phone: str) -> str:
        """
        Add a new contact or update existing contact with phone number.
        
        Args:
            name: Contact name
            phone: Phone number (10 digits)
            
        Returns:
            Success message
            
        Raises:
            ValueError: If phone format is invalid
        """
        record = self.address_book.find(name)
        message = "Contact updated."
        if record is None:
            record = Record(name)
            self.address_book.add_record(record)
            message = "Contact added."
        if phone:
            record.add_phone(phone)
        return message
    
    def change_contact(self, name: str, old_phone: str, new_phone: str) -> str:
        """
        Change an existing contact's phone number.
        
        Args:
            name: Contact name
            old_phone: Old phone number
            new_phone: New phone number
            
        Returns:
            Success message
            
        Raises:
            ValueError: If contact not found or phone invalid
        """
        record = self.address_book.find(name)
        if record is None:
            raise ValueError(f"Contact '{name}' not found.")
        
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    
    def get_phone(self, name: str) -> str:
        """
        Get phone numbers for a specific contact.
        
        Args:
            name: Contact name
            
        Returns:
            Phone numbers separated by semicolons
            
        Raises:
            ValueError: If contact not found
        """
        record = self.address_book.find(name)
        if record is None:
            raise ValueError(f"Contact '{name}' not found.")
        
        if not record.phones:
            return f"No phones for contact '{name}'."
        
        return '; '.join(p.value for p in record.phones)
    
    def get_all_contacts(self) -> str:
        """
        Get all contacts as a formatted string.
        
        Returns:
            Formatted string with all contacts or message if no contacts exist
        """
        return str(self.address_book)
    
    def add_birthday(self, name: str, birthday: str) -> str:
        """
        Add birthday to a contact.
        
        Args:
            name: Contact name
            birthday: Birthday in DD.MM.YYYY format
            
        Returns:
            Success message
            
        Raises:
            ValueError: If contact not found or date format invalid
        """
        record = self.address_book.find(name)
        if record is None:
            raise ValueError(f"Contact '{name}' not found.")
        
        record.add_birthday(birthday)
        return "Birthday added."
    
    def get_birthday(self, name: str) -> str:
        """
        Get birthday for a specific contact.
        
        Args:
            name: Contact name
            
        Returns:
            Birthday date
            
        Raises:
            ValueError: If contact not found
        """
        record = self.address_book.find(name)
        if record is None:
            raise ValueError(f"Contact '{name}' not found.")
        
        if record.birthday is None:
            return f"No birthday set for contact '{name}'."
        
        return str(record.birthday)
    
    def get_upcoming_birthdays(self, days: int = 7) -> str:
        """
        Get upcoming birthdays for the next week.
        
        Args:
            days: Number of days ahead to check (default: 7)
        
        Returns:
            Formatted list of upcoming birthdays or message if none
        """
        upcoming = self._calculate_upcoming_birthdays(days)
        
        if not upcoming:
            return "No upcoming birthdays in the next week."
        
        result = []
        for entry in upcoming:
            result.append(f"{entry['name']}: {entry['congratulation_date']}")
        
        return "\n".join(result)
    
    def _calculate_upcoming_birthdays(self, days: int = 7) -> list[dict]:
        """
        Calculate list of contacts with upcoming birthdays.
        
        This is business logic that determines which birthdays are upcoming
        and adjusts congratulation dates for weekends.
        
        Args:
            days: Number of days ahead to check (default: 7)
            
        Returns:
            List of dictionaries with name and congratulation_date keys
            
        Example:
            [{"name": "John", "congratulation_date": "01.01.2024"}]
        """
        upcoming = []
        today = datetime.today().date()
        
        for record in self.address_book.data.values():
            if record.birthday is None:
                continue
            
            birthday_date = record.birthday.date.date()
            birthday_this_year = birthday_date.replace(year=today.year)
            
            if birthday_this_year < today:
                birthday_this_year = birthday_date.replace(year=today.year + 1)
            
            days_until_birthday = (birthday_this_year - today).days
            
            if 0 <= days_until_birthday <= days:
                congratulation_date = birthday_this_year
                
                if congratulation_date.weekday() >= 5:
                    days_until_monday = 7 - congratulation_date.weekday()
                    congratulation_date += timedelta(days=days_until_monday)
                
                upcoming.append({
                    "name": record.name.value,
                    "congratulation_date": congratulation_date.strftime("%d.%m.%Y")
                })
        
        return upcoming
    
    def has_contacts(self) -> bool:
        """
        Check if address book has any contacts.
        
        Returns:
            True if address book has contacts, False otherwise
        """
        return len(self.address_book.data) > 0




