"""
Tests for ContactService.

This module contains comprehensive tests for all contact service operations.
"""

import pytest
from datetime import datetime, timedelta
from src.models.address_book import AddressBook
from src.models.record import Record
from src.services.contact_service import ContactService, ContactSortBy
from src.models.group import DEFAULT_GROUP_ID


@pytest.fixture
def address_book():
    """Create an empty address book for testing."""
    return AddressBook()


@pytest.fixture
def contact_service(address_book):
    """Create a contact service with an empty address book."""
    return ContactService(address_book)


@pytest.fixture
def populated_service():
    """Create a contact service with some test data."""
    book = AddressBook()
    record = Record("John")
    record.add_phone("1234567890")
    record.add_birthday("15.05.1990")
    book.add_record(record)
    return ContactService(book)

@pytest.fixture
def sorting_service():
    """Create a contact service with multiple contacts for sorting tests."""
    book = AddressBook()

    pavlo = Record("Pavlo")
    pavlo.add_phone("3333333333")
    pavlo.add_birthday("15.05.1990")
    pavlo.add_tag("ml")
    pavlo.add_tag("ai")
    book.add_record(pavlo)

    anna = Record("Anna")
    anna.add_phone("1111111111")
    anna.add_birthday("01.01.1980")
    anna.add_tag("ai")
    book.add_record(anna)

    illia = Record("Illia")
    illia.add_phone("2222222222")
    # no birthday, no tags
    book.add_record(illia)

    return ContactService(book)


class TestAddContact:
    """Tests for add_contact method."""
    
    def test_add_new_contact(self, contact_service):
        """Test adding a new contact."""
        result = contact_service.add_contact("Alice", "1234567890")
        assert result == "Contact added."
        assert contact_service.address_book.find("Alice") is not None
    
    def test_add_phone_to_existing_contact(self, populated_service):
        """Test adding a phone to an existing contact."""
        result = populated_service.add_contact("John", "0987654321")
        assert result == "Contact updated."
        record = populated_service.address_book.find("John")
        assert len(record.phones) == 2
    
    def test_add_contact_with_invalid_phone(self, contact_service):
        """Test adding a contact with invalid phone number."""
        with pytest.raises(ValueError):
            contact_service.add_contact("Bob", "invalid")


class TestChangeContact:
    """Tests for change_contact method."""
    
    def test_change_existing_phone(self, populated_service):
        """Test changing an existing phone number."""
        result = populated_service.change_contact("John", "1234567890", "0987654321")
        assert result == "Contact updated."
        record = populated_service.address_book.find("John")
        assert record.find_phone("0987654321") is not None
        assert record.find_phone("1234567890") is None
    
    def test_change_phone_contact_not_found(self, contact_service):
        """Test changing phone for non-existent contact."""
        with pytest.raises(ValueError, match="not found"):
            contact_service.change_contact("NonExistent", "1234567890", "0987654321")
    
    def test_change_phone_number_not_found(self, populated_service):
        """Test changing a phone number that doesn't exist."""
        with pytest.raises(ValueError):
            populated_service.change_contact("John", "9999999999", "0987654321")


class TestGetPhone:
    """Tests for get_phone method."""
    
    def test_get_phone_for_existing_contact(self, populated_service):
        """Test getting phone for existing contact."""
        result = populated_service.get_phone("John")
        assert "1234567890" in result
    
    def test_get_phone_contact_not_found(self, contact_service):
        """Test getting phone for non-existent contact."""
        with pytest.raises(ValueError, match="not found"):
            contact_service.get_phone("NonExistent")
    
    def test_get_phone_no_phones(self, contact_service):
        """Test getting phone for contact with no phones."""
        service = contact_service
        record = Record("NoPhone")
        service.address_book.add_record(record)
        result = service.get_phone("NoPhone")
        assert "No phones" in result


class TestGetAllContacts:
    """Tests for get_all_contacts method."""
    
    def test_get_all_contacts_empty(self, contact_service):
        """Test getting all contacts when address book is empty."""
        result = contact_service.get_all_contacts()
        assert "Address book is empty" in result or result == ""
    
    def test_get_all_contacts_populated(self, populated_service):
        """Test getting all contacts with data."""
        result = populated_service.get_all_contacts()
        assert "John" in result
        assert "1234567890" in result


class TestBirthday:
    """Tests for birthday-related methods."""
    
    def test_add_birthday(self, contact_service):
        """Test adding a birthday to a contact."""
        contact_service.add_contact("Alice", "1234567890")
        result = contact_service.add_birthday("Alice", "10.03.1995")
        assert result == "Birthday added."
    
    def test_add_birthday_contact_not_found(self, contact_service):
        """Test adding birthday to non-existent contact."""
        with pytest.raises(ValueError, match="not found"):
            contact_service.add_birthday("NonExistent", "10.03.1995")
    
    def test_add_birthday_invalid_format(self, contact_service):
        """Test adding birthday with invalid format."""
        contact_service.add_contact("Alice", "1234567890")
        with pytest.raises(ValueError):
            contact_service.add_birthday("Alice", "invalid-date")
    
    def test_get_birthday(self, populated_service):
        """Test getting birthday for a contact."""
        result = populated_service.get_birthday("John")
        assert "15.05.1990" in result
    
    def test_get_birthday_not_set(self, contact_service):
        """Test getting birthday when not set."""
        contact_service.add_contact("Alice", "1234567890")
        result = contact_service.get_birthday("Alice")
        assert "No birthday set" in result
    
    def test_get_birthday_contact_not_found(self, contact_service):
        """Test getting birthday for non-existent contact."""
        with pytest.raises(ValueError, match="not found"):
            contact_service.get_birthday("NonExistent")
    
    def test_get_upcoming_birthdays_none(self, contact_service):
        """Test getting upcoming birthdays when none exist."""
        result = contact_service.get_upcoming_birthdays()
        assert "No upcoming birthdays" in result
    
    def test_get_upcoming_birthdays_within_week(self, contact_service):
        """Test getting birthdays within the next week."""
        contact_service.add_contact("John", "1234567890")
        
        today = datetime.today().date()
        birthday_in_5_days = today + timedelta(days=5)
        birthday_str = birthday_in_5_days.strftime("%d.%m.2000")
        
        contact_service.add_birthday("John", birthday_str)
        
        result = contact_service.get_upcoming_birthdays()
        assert "John" in result
        assert "No upcoming birthdays" not in result
    
    def test_get_upcoming_birthdays_today(self, contact_service):
        """Test that get_upcoming_birthdays includes today's birthday."""
        contact_service.add_contact("John", "1234567890")
        
        today = datetime.today().date()
        birthday_str = today.strftime("%d.%m.2000")
        
        contact_service.add_birthday("John", birthday_str)
        
        result = contact_service.get_upcoming_birthdays()
        assert "John" in result
    
    def test_get_upcoming_birthdays_past_birthday(self, contact_service):
        """Test that get_upcoming_birthdays excludes past birthdays."""
        contact_service.add_contact("John", "1234567890")
        
        today = datetime.today().date()
        birthday_yesterday = today - timedelta(days=1)
        birthday_str = birthday_yesterday.strftime("%d.%m.2000")
        
        contact_service.add_birthday("John", birthday_str)
        
        result = contact_service.get_upcoming_birthdays()
        assert "No upcoming birthdays" in result
    
    def test_get_upcoming_birthdays_too_far_in_future(self, contact_service):
        """Test that get_upcoming_birthdays excludes birthdays more than 7 days away."""
        contact_service.add_contact("John", "1234567890")
        
        today = datetime.today().date()
        birthday_in_8_days = today + timedelta(days=8)
        birthday_str = birthday_in_8_days.strftime("%d.%m.2000")
        
        contact_service.add_birthday("John", birthday_str)
        
        result = contact_service.get_upcoming_birthdays()
        assert "No upcoming birthdays" in result
    
    def test_get_upcoming_birthdays_multiple_contacts(self, contact_service):
        """Test that get_upcoming_birthdays returns multiple contacts."""
        today = datetime.today().date()
        
        contact_service.add_contact("John", "1234567890")
        john_birthday = (today + timedelta(days=2)).strftime("%d.%m.2000")
        contact_service.add_birthday("John", john_birthday)
        
        contact_service.add_contact("Jane", "0987654321")
        jane_birthday = (today + timedelta(days=5)).strftime("%d.%m.2000")
        contact_service.add_birthday("Jane", jane_birthday)
        
        result = contact_service.get_upcoming_birthdays()
        assert "John" in result
        assert "Jane" in result
    
    def test_get_upcoming_birthdays_weekend_adjustment(self, contact_service):
        """Test that birthdays on weekends are moved to Monday."""
        contact_service.add_contact("John", "1234567890")
        
        today = datetime.today().date()
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0:
            days_until_saturday = 7
        
        next_saturday = today + timedelta(days=days_until_saturday)
        birthday_str = next_saturday.strftime("%d.%m.2000")
        
        if days_until_saturday <= 7:
            contact_service.add_birthday("John", birthday_str)
            result = contact_service.get_upcoming_birthdays()
            
            if "John" in result:
                lines = result.split('\n')
                for line in lines:
                    if "John" in line:
                        date_str = line.split(': ')[1]
                        congratulation_date = datetime.strptime(date_str, "%d.%m.%Y").date()
                        assert congratulation_date.weekday() == 0
    
    def test_get_upcoming_birthdays_custom_days(self, contact_service):
        """Test that get_upcoming_birthdays accepts custom days parameter."""
        contact_service.add_contact("John", "1234567890")
        
        today = datetime.today().date()
        birthday_in_10_days = today + timedelta(days=10)
        birthday_str = birthday_in_10_days.strftime("%d.%m.2000")
        
        contact_service.add_birthday("John", birthday_str)
        
        result_7_days = contact_service.get_upcoming_birthdays(days=7)
        assert "No upcoming birthdays" in result_7_days
        
        result_14_days = contact_service.get_upcoming_birthdays(days=14)
        assert "John" in result_14_days


class TestHasContacts:
    """Tests for has_contacts method."""
    
    def test_has_contacts_empty(self, contact_service):
        """Test has_contacts with empty address book."""
        assert contact_service.has_contacts() is False
    
    def test_has_contacts_populated(self, populated_service):
        """Test has_contacts with populated address book."""
        assert populated_service.has_contacts() is True

class TestSorting:
    """Tests for contact sorting logic."""

    def test_list_contacts_sort_by_name(self, sorting_service):
        """Contacts are sorted alphabetically by name (case-insensitive)."""
        items = sorting_service.list_contacts(sort_by=ContactSortBy.NAME)
        names = [name for name, _ in items]
        assert names == ["Anna", "Illia", "Pavlo"]

    def test_list_contacts_sort_by_phone(self, sorting_service):
        """Contacts are sorted by first phone number."""
        items = sorting_service.list_contacts(sort_by=ContactSortBy.PHONE)
        names = [name for name, _ in items]
        # 1111111111 < 2222222222 < 3333333333
        assert names == ["Anna", "Illia", "Pavlo"]

    def test_list_contacts_sort_by_birthday(self, sorting_service):
        """Contacts are sorted by birthday, contacts without birthday go last."""
        items = sorting_service.list_contacts(sort_by=ContactSortBy.BIRTHDAY)
        names = [name for name, _ in items]
        # Anna: 01.01.1980, Pavlo: 15.05.1990, Illia: no birthday -> last
        assert names == ["Anna", "Pavlo", "Illia"]

    def test_list_contacts_sort_by_tag_count(self, sorting_service):
        """Contacts are sorted by tag count in descending order."""
        items = sorting_service.list_contacts(sort_by=ContactSortBy.TAG_COUNT)
        names = [name for name, _ in items]
        # Pavlo: 2 tags, Anna: 1 tag, Illia: 0 tags
        assert names == ["Pavlo", "Anna", "Illia"]

    def test_list_contacts_sort_by_tag_name(self, sorting_service):
        """
        Contacts are sorted by tag names; contacts without tags use empty string
        and therefore go first.
        """
        items = sorting_service.list_contacts(sort_by=ContactSortBy.TAG_NAME)
        names = [name for name, _ in items]
        # Illia: no tags -> key="", Anna: "ai", Pavlo: "ai,ml"/"ml,ai" -> above Anna
        assert names[0] == "Illia"
        assert names.index("Anna") < names.index("Pavlo")

    def test_get_all_contacts_uses_list_contacts_sorting(self, sorting_service, monkeypatch):
        """get_all_contacts should respect sort_by and use list_contacts under the hood."""
        calls = []

        def fake_list_contacts(sort_by, group=None):
            calls.append((sort_by, group))
            return [("X", sorting_service.address_book.find("Pavlo"))]

        monkeypatch.setattr(sorting_service, "list_contacts", fake_list_contacts)

        result = sorting_service.get_all_contacts(sort_by=ContactSortBy.NAME)
        assert "Contact name: X" in result
        # sort_by exist, group by default None
        assert calls == [(ContactSortBy.NAME, None)]

class TestGroupsService:
    """Tests for groups support in ContactService."""

    def test_list_groups_has_default_personal(self, contact_service):
        """Empty address book has only default group with zero contacts."""
        groups = contact_service.list_groups()
        assert groups  # not empty
        ids = [gid for gid, _ in groups]
        assert DEFAULT_GROUP_ID in ids
        # default has 0 contacts
        default_entry = next((c for c in groups if c[0] == DEFAULT_GROUP_ID), None)
        assert default_entry is not None
        assert default_entry[1] == 0

    def test_add_group_creates_new_group(self, contact_service):
        """add_group registers new group in address book."""
        contact_service.add_group("work")
        groups = contact_service.list_groups()
        ids = {gid for gid, _ in groups}
        assert {DEFAULT_GROUP_ID, "work"} <= ids
        assert contact_service.address_book.has_group("work")

    def test_add_group_duplicate_raises(self, contact_service):
        """add_group fails on duplicate group id."""
        contact_service.add_group("work")
        with pytest.raises(ValueError):
            contact_service.add_group("work")

    def test_set_current_group_success(self, contact_service):
        """set_current_group switches active group."""
        contact_service.add_group("work")
        contact_service.set_current_group("work")
        assert contact_service.get_current_group() == "work"

    def test_set_current_group_not_found(self, contact_service):
        """set_current_group fails for unknown group."""
        with pytest.raises(ValueError, match="not found"):
            contact_service.set_current_group("unknown")

    def test_add_contact_uses_current_group_by_default(self, contact_service):
        """add_contact without explicit group uses current_group_id."""
        contact_service.add_group("work")
        contact_service.set_current_group("work")

        contact_service.add_contact("Alice", "1234567890")

        # find created record
        records = list(contact_service.address_book.data.values())
        rec = next(r for r in records if r.name.value == "Alice")
        assert rec.group_id == "work"

    def test_add_contact_explicit_group_overrides_current(self, contact_service):
        """Explicit group_id in add_contact overrides current group."""
        contact_service.add_group("work")
        contact_service.set_current_group("work")

        contact_service.add_contact("Bob", "1234567890", group_id="other")

        records = list(contact_service.address_book.data.values())
        rec = next(r for r in records if r.name.value == "Bob")
        assert rec.group_id == "other"
        # group 'other' should also be registered in address book
        assert contact_service.address_book.has_group("other")

class TestGroupsFiltering:
    """Tests for group-based filtering in list_contacts/get_all_contacts."""

    def test_list_contacts_filters_by_current_group(self, contact_service):
        contact_service.add_group("work")
        # current group = personal (DEFAULT)
        contact_service.add_contact("Alice", "1111111111")  # personal
        contact_service.set_current_group("work")
        contact_service.add_contact("Bob", "2222222222")    # work

        items = contact_service.list_contacts()  # default -> current (work)
        names = [name for name, _ in items]
        assert names == ["Bob"]

    def test_list_contacts_filters_by_specific_group(self, contact_service):
        contact_service.add_group("work")
        contact_service.add_contact("Alice", "1111111111", group_id="personal")
        contact_service.add_contact("Bob", "2222222222", group_id="work")

        items_personal = contact_service.list_contacts(group="personal")
        names_personal = [name for name, _ in items_personal]
        assert names_personal == ["Alice"]

        items_work = contact_service.list_contacts(group="work")
        names_work = [name for name, _ in items_work]
        assert names_work == ["Bob"]

    def test_list_contacts_all_groups(self, contact_service):
        contact_service.add_group("work")
        contact_service.add_contact("Alice", "1111111111", group_id="personal")
        contact_service.add_contact("Bob", "2222222222", group_id="work")

        items_all = contact_service.list_contacts(group="all")
        names_all = [name for name, _ in items_all]
        assert set(names_all) == {"Alice", "Bob"}

    def test_get_all_contacts_group_all_grouped_output(self, contact_service):
        contact_service.add_group("work")
        contact_service.add_contact("Alice", "1111111111", group_id="personal")
        contact_service.add_contact("Bob", "2222222222", group_id="work")

        out = contact_service.get_all_contacts(group="all")

        # group header exists
        assert "Group: personal" in out
        assert "Group: work" in out
        # names exists
        assert "Alice" in out
        assert "Bob" in out

        # Alice has to be inside "personal" group
        personal_block = out.split("Group: personal", 1)[1].split("Group:", 1)[0]
        assert "Alice" in personal_block

        # Bob has to be inside "work" group
        work_block = out.split("Group: work", 1)[1]
        assert "Bob" in work_block

    def test_list_contacts_unknown_group_raises(self, contact_service):
        with pytest.raises(ValueError, match="Group 'unknown' not found"):
            contact_service.list_contacts(group="unknown")

class TestGroupsIsolation:
    """Tests that contacts with the same name are isolated per group."""

    def _get_phones_by_group(self, service: ContactService, name: str) -> dict[str, list[str]]:
        """Helper: {group_id: [phones]} for a given name."""
        result: dict[str, list[str]] = {}
        for rec in service.address_book.data.values():
            if rec.name.value != name:
                continue
            gid = rec.group_id
            result.setdefault(gid, []).extend(p.value for p in rec.phones)
        return result

    def test_get_phone_uses_current_group(self, contact_service):
        """get_phone should read contact from current group only."""
        svc = contact_service
        svc.add_group("work")

        # same name in two groups
        svc.add_contact("John", "1111111111", group_id="personal")
        svc.add_contact("John", "2222222222", group_id="work")

        # personal
        svc.set_current_group("personal")
        out = svc.get_phone("John")
        assert "1111111111" in out
        assert "2222222222" not in out

        # work
        svc.set_current_group("work")
        out = svc.get_phone("John")
        assert "2222222222" in out
        assert "1111111111" not in out

    def test_change_contact_affects_only_current_group(self, contact_service):
        """change_contact must update record only in current group."""
        svc = contact_service
        svc.add_group("work")

        svc.add_contact("John", "1111111111", group_id="personal")
        svc.add_contact("John", "2222222222", group_id="work")

        # change in personal
        svc.set_current_group("personal")
        svc.change_contact("John", "1111111111", "3333333333")

        phones = self._get_phones_by_group(svc, "John")
        assert sorted(phones["personal"]) == ["3333333333"]
        assert sorted(phones["work"]) == ["2222222222"]

    def test_tags_are_isolated_per_group(self, contact_service):
        """Tag operations for the same name are scoped to current group."""
        svc = contact_service
        svc.add_group("work")

        svc.add_contact("John", "1111111111", group_id="personal")
        svc.add_contact("John", "2222222222", group_id="work")

        # personal: add and verify
        svc.set_current_group("personal")
        svc.add_tag("John", "friends")
        assert svc.list_tags("John") == ["friends"]

        # work: separate tags
        svc.set_current_group("work")
        svc.add_tag("John", "colleague")
        assert svc.list_tags("John") == ["colleague"]

        # back to personal: tags должны остаться только свои
        svc.set_current_group("personal")
        assert svc.list_tags("John") == ["friends"]

    def test_clear_tags_only_in_current_group(self, contact_service):
        """clear_tags should clear tags only for record in current group."""
        svc = contact_service
        svc.add_group("work")

        svc.add_contact("John", "1111111111", group_id="personal")
        svc.add_contact("John", "2222222222", group_id="work")

        svc.set_current_group("personal")
        svc.add_tag("John", "friends")

        svc.set_current_group("work")
        svc.add_tag("John", "colleague")

        # clear only in work
        svc.clear_tags("John")

        svc.set_current_group("personal")
        assert svc.list_tags("John") == ["friends"]

        svc.set_current_group("work")
        assert svc.list_tags("John") == []
