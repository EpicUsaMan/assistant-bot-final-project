"""
Contact service for managing contacts in the address book.

This service provides business logic for contact operations with proper
separation of concerns and dependency injection support.
"""

from datetime import datetime, timedelta
from typing import Callable, Dict, Iterable, List, Optional, Tuple, Any

from src.models.address_book import AddressBook
from src.models.record import Record
from src.models.tags import Tags
from src.utils.validators import is_valid_tag, normalize_tag, split_tags_string
from enum import Enum

#--- Contact sorting options ---
class ContactSortBy(str, Enum):
    '''
        Enum for contact sorting criteria.
        Attributes:
            NAME: Sort by contact name
            PHONE: Sort by phone number
            BIRTHDAY: Sort by birthday date
            TAG_COUNT: Sort by number of tags
            TAG_NAME: Sort by tag names
    '''
    NAME = "name"
    PHONE = "phone"
    BIRTHDAY = "birthday"    
    TAG_COUNT = "tag_count"
    TAG_NAME = "tag_name"

class ContactService:
    """
    Service for managing contacts in an address book.

    This class encapsulates all business logic for contact operations,
    making it easy to test and inject dependencies.
    """

    DEFAULT_SORT_BY: ContactSortBy = ContactSortBy.NAME

    # mapping: sort mode -> (key_fn, reverse_flag)
    _SORTING_STRATEGIES: dict[ContactSortBy, tuple[Callable[[Tuple[str, Record]], Any], bool]] = {
        ContactSortBy.NAME: (
            lambda kv: kv[0].lower(),
            False,
        ),
        ContactSortBy.PHONE: (
            lambda kv: kv[1].phones[0].value if kv[1].phones else "",
            False,
        ),
        ContactSortBy.BIRTHDAY: (
            lambda kv: (
                kv[1].birthday.date.date()
                if kv[1].birthday
                else datetime.max.date()
            ),
            False,
        ),
        ContactSortBy.TAG_COUNT: (
            lambda kv: len(kv[1].tags_list()),
            True,  # descending
        ),
        ContactSortBy.TAG_NAME: (
            lambda kv: ",".join(kv[1].tags_list()).lower(),
            False,
        ),
    }    

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

        return "; ".join(p.value for p in record.phones)

    def get_all_contacts(self, sort_by: "ContactSortBy | None" = None) -> str:
        """
        Get all contacts as a formatted string.

        Args:
            sort_by: Sorting criteria (or None for no sorting)

        Returns:
            Formatted string with all contacts or message if no contacts exist
        """
        items = self.list_contacts(sort_by=sort_by)

        if not items:
            return "Address book is empty."

        lines: list[str] = []
        for name, rec in items:
            phones = "; ".join(p.value for p in rec.phones) if rec.phones else ""
            tags = ", ".join(rec.tags_list())
            line = f"Contact name: {name}, phones: {phones}"
            if tags:
                line += f", tags: {tags}"
            lines.append(line)

        # double newlines between contacts as in CLI output
        return "\n\n".join(lines)

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

                upcoming.append(
                    {
                        "name": record.name.value,
                        "congratulation_date": congratulation_date.strftime("%d.%m.%Y"),
                    }
                )

        return upcoming

    def has_contacts(self) -> bool:
        """
        Check if address book has any contacts.

        Returns:
            True if address book has contacts, False otherwise
        """
        return len(self.address_book.data) > 0

    def list_contacts(
            self, 
            sort_by: "ContactSortBy | None" = None,
        ) -> List[Tuple[str, Record]]:
        """
        Return [(name, record)] optionally sorted.

        Args:
            sort_by: Sorting criteria

        Returns:
            List of (name, record) tuples
        """

        items = list(self.address_book.data.items())

        sorting = self._SORTING_STRATEGIES
        effective_sort_by = sort_by or self.DEFAULT_SORT_BY

        key_fn, reverse = sorting.get(
            effective_sort_by,
            sorting[self.DEFAULT_SORT_BY],
        )

        items.sort(key=key_fn, reverse=reverse)
        return items

    # --- Tags management ---
    def add_tag(self, name: str, tag: str) -> str:
        """
        Add a tag to a contact.
        Args:
            name: Contact name
            tag: Tag to add
        Returns:
            Success message
        """
        record = self.address_book.find(name)
        if record is None:
            raise ValueError(f"Contact '{name}' not found.")
        n = normalize_tag(tag)
        if not is_valid_tag(n):
            raise ValueError(f"Invalid tag: '{tag}'")
        record.add_tag(n)
        message = f"Tag '{n}' added to {name}."

        return message

    def remove_tag(self, name: str, tag: str) -> str:
        """
        Remove a tag from a contact.
        Args:
            name: Contact name
            tag: Tag to remove
        """
        record = self.address_book.find(name)
        if record is None:
            raise ValueError(f"Contact '{name}' not found.")
        n = normalize_tag(tag)
        record.remove_tag(n)
        message = f"Tag '{n}' removed from {name}."
        return message

    def clear_tags(self, name: str) -> str:
        """
        Clear all tags from a contact.
        Args:
            name: Contact name
        """
        record = self.address_book.find(name)
        if record is None:
            raise ValueError(f"Contact '{name}' not found.")
        record.clear_tags()
        message = f"All tags cleared for {name}."
        return message

    def list_tags(self, name: str) -> list[str]:
        """
        List all tags for a contact.
        Args:
            name: Contact name
        """
        record = self.address_book.find(name)
        if record is None:
            raise ValueError(f"Contact '{name}' not found.")
        return record.tags.as_list()

    # --- helpers ---
    def _iter_name_record(self) -> Iterable[Tuple[str, "Record"]]:
        book = self.address_book
        if hasattr(book, "data") and isinstance(book.data, dict):
            return book.data.items()
        raise RuntimeError("AddressBook storage not recognized")

    def _prepare_tags(self, tags: List[str] | str) -> List[str]:
        if isinstance(tags, str):
            tags = split_tags_string(tags)
        out = []
        for t in tags:
            n = normalize_tag(t)
            if not n or not is_valid_tag(n):
                raise ValueError(f"Invalid tag: '{t}'")
            out.append(n)
        return out
    
    # --- search by tags ---
    def find_by_tags_all(self, tags: List[str] | str) -> List[Tuple[str, "Record"]]:
        """
        returns contacts that have *all* specified tags (AND).
        """
        want = set(self._prepare_tags(tags))
        if not want:
            return []
        result: List[Tuple[str, "Record"]] = []
        for name, rec in self._iter_name_record():
            have = set(rec.tags_list())
            if want.issubset(have):
                result.append((name, rec))
        return result

    def find_by_tags_any(self, tags: List[str] | str) -> List[Tuple[str, "Record"]]:
        """
        returns contacts that have *at least one* of the specified tags (OR).
        """
        want = set(self._prepare_tags(tags))
        if not want:
            return []
        result: List[Tuple[str, "Record"]] = []
        for name, rec in self._iter_name_record():
            have = set(rec.tags_list())
            if want & have:
                result.append((name, rec))
        return result
