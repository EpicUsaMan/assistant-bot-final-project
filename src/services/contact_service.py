"""
Contact service for managing contacts in the address book.

This service provides business logic for contact operations with proper
separation of concerns and dependency injection support.
"""

from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Optional, Tuple, Any, Callable

from src.models.address_book import AddressBook
from src.models.record import Record
from src.models.tags import Tags
from src.models.group import Group, DEFAULT_GROUP_ID, normalize_group_id
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

    def add_contact(
        self,
        name: str,
        phone: str,
        group_id: str | None = None,
    ) -> str:
        """
        Add a new contact or update existing contact within a group.

        Args:
            name: Contact name
            phone: Phone number (10 digits)
            group_id: Optional explicit group, defaults to current_group_id

        Returns:
            Success message
        """
        gid = group_id or self.address_book.current_group_id

        # if no such group - create
        if not self.address_book.has_group(gid):            
            self.address_book.add_group(gid)

        record = self.address_book.find(name, group_id=gid)
        message = "Contact updated."
        if record is None:
            record = Record(name, group_id=gid)
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

        return "; ".join(p.display_value for p in record.phones)

    def get_all_contacts(
        self,
        sort_by: "ContactSortBy | None" = None,
        group: str | None = None,
    ) -> str:
        """
        Get contacts as a formatted string.

        Args:
            sort_by: Sorting criteria
            group: Group filter:
                None / "current" – only current group
                "all" – all groups (grouped in output)
                <group_id> – specific group
        """
        if group != "all":
            items = self.list_contacts(sort_by=sort_by, group=group)
            if not items:
                return "Address book is empty."

            lines: list[str] = []
            for name, rec in items:
                phones = "; ".join(p.display_value for p in rec.phones) if rec.phones else ""
                tags = ", ".join(rec.tags_list())
                line = f"Contact name: {name}, phones: {phones}"
                if tags:
                    line += f", tags: {tags}"
                lines.append(line)
            return "\n\n".join(lines)

        all_lines: list[str] = []        
        
        for group_obj  in self.address_book.iter_groups():
            # contacts in this group sorted
            gid = group_obj.id
            items = self.list_contacts(sort_by=sort_by, group=gid)
            if not items:
                continue

            # group header
            all_lines.append(f"Group: {gid}")

            # contacts in group
            for name, rec in items:
                phones = "; ".join(p.display_value for p in rec.phones) if rec.phones else ""
                tags = ", ".join(rec.tags_list())
                line = f"  Contact name: {name}, phones: {phones}"
                if tags:
                    line += f", tags: {tags}"
                all_lines.append(line)

            # separator
            all_lines.append("")

        # when no contacts
        if not all_lines:
            return "Address book is empty."

        # remove last divider
        if all_lines and all_lines[-1] == "":
            all_lines.pop()

        return "\n".join(all_lines)


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
            group: str | None = None,
        ) -> List[Tuple[str, Record]]:
        """
        Return [(name, record)] optionally sorted and filtered by groups.

        Args:
            sort_by: Sorting criteria
            group: Group filter:
                None / "current" (default) – only current group
                "all" – all groups
                <group_id> – specific group
        """

        gid = group or self.address_book.current_group_id
        if gid != "all" and not self.address_book.has_group(gid):
            raise ValueError(f"Group '{gid}' not found")        

        if gid == "all":
            items = self.address_book.iter_all()
        else:
            items = self.address_book.iter_group(gid)

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

    # --- Groups management ---
    @property
    def current_group_id(self) -> str:
        """Current active group id stored in AddressBook."""
        return getattr(self.address_book, "current_group_id", DEFAULT_GROUP_ID)
    
    def set_current_group(self, group_id: str) -> None:
        """
        Switch active group.

        Raises:
            ValueError: if group does not exist.
        """
        gid = normalize_group_id(group_id)
        if not self.address_book.has_group(gid):
            raise ValueError(f"Group '{gid}' not found.")
        self.address_book.current_group_id = gid

    def get_current_group(self) -> str:
        return self.current_group_id    

    def list_groups(self) -> list[tuple[str, int]]:
        """
        Returns: list of (group_id, contacts_count) sorted by group_id.
        """
        result: list[tuple[str, int]] = []
        for group in self.address_book.iter_groups():
            count = sum(
                1
                for rec in self.address_book.data.values()
                if getattr(rec, "group_id", DEFAULT_GROUP_ID) == group.id
            )
            result.append((group.id, count))
        return result

    def add_group(self, group_id: str, title: str | None = None) -> None:
        """
        Create new group.

        Raises:
            ValueError: if group id invalid or already exists.
        """
        self.address_book.add_group(group_id, title)

    def rename_group(self, old_id: str, new_id: str) -> str:
        self.address_book.rename_group(old_id, new_id)
        return f"Group '{old_id}' renamed to '{new_id}'."

    def remove_group(self, group_id: str, force: bool = False) -> str:
        self.address_book.remove_group(group_id, force=force)
        if force:
            return f"Group '{group_id}' and its contacts removed."
        return f"Group '{group_id}' removed."        