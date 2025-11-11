"""
Tests for ContactService.

This module contains comprehensive tests for all contact service operations.
"""

import pytest
from datetime import datetime, timedelta
from src.models.address_book import AddressBook
from src.models.record import Record
from src.services.contact_service import ContactService, ContactSortBy


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

        def fake_list_contacts(sort_by):
            calls.append(sort_by)
            # return in sorted order to verify output
            return [("X", sorting_service.address_book.find("Pavlo"))]

        monkeypatch.setattr(sorting_service, "list_contacts", fake_list_contacts)

        result = sorting_service.get_all_contacts(sort_by=ContactSortBy.NAME)
        assert "Contact name: X" in result
        # to be sure, that sort_by is passed to list_contacts
        assert calls == [ContactSortBy.NAME]



