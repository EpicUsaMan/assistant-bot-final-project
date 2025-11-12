"""
Tests for CLI commands.

This module contains comprehensive tests for all CLI commands using
Typer's CliRunner and mocked dependencies.

Tests cover:
- Command functionality
- Parameter validation (Typer callbacks)
- Service error handling
- Auto-save functionality for UPDATE commands
"""

import pytest
from typer.testing import CliRunner
from unittest.mock import Mock, patch
from src.main import app, container
from src.models.address_book import AddressBook
from src.models.record import Record
from src.services.contact_service import ContactService, ContactSortBy


runner = CliRunner()


# Module-level setup - register commands once for all tests
import src.main
src.main.auto_register_commands()


@pytest.fixture(autouse=True)
def setup_container():
    """Set up the DI container before each test."""
    container.config.storage.filename.from_value("test_addressbook.pkl")
    # Wire the container before each test to ensure @inject decorators work
    if not src.main._container_wired:
        command_modules = [
            'src.commands.add',
            'src.commands.change',
            'src.commands.phone',
            'src.commands.all',
            'src.commands.add_birthday',
            'src.commands.show_birthday',
            'src.commands.birthdays',
        ]
        container.wire(modules=command_modules)
        src.main._container_wired = True
    yield
    # No unwiring between tests - keep the wiring active


@pytest.fixture
def mock_service():
    """Create a mock contact service."""
    service = Mock(spec=ContactService)
    # Add mock address_book attribute with save_to_file method
    service.address_book = Mock()
    service.address_book.save_to_file = Mock()
    return service


class TestHelloCommand:
    """Tests for hello command."""
    
    def test_hello(self):
        """Test hello command."""
        result = runner.invoke(app, ["hello"])
        assert result.exit_code == 0
        assert "How can I help you?" in result.stdout


class TestAddCommand:
    """Tests for add command."""
    
    def test_add_new_contact_success(self, mock_service):
        """Test adding a new contact successfully."""
        mock_service.add_contact.return_value = "Contact added."
        
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["add", "John", "0123456789"])
            
        assert result.exit_code == 0
        assert "Contact added" in result.stdout
        mock_service.add_contact.assert_called_once_with("John", "+380123456789")
        mock_service.address_book.save_to_file.assert_called_once()
    
    def test_add_contact_invalid_phone_format_not_digits(self, mock_service):
        """Test adding contact with non-digit phone (caught by validator)."""
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["add", "John", "invalid"])
            
        assert result.exit_code == 2
        output = result.output
        assert "Invalid value for 'PHONE'" in result.output
        mock_service.add_contact.assert_not_called()
    
    def test_add_contact_invalid_phone_format_wrong_length(self, mock_service):
        """Test adding contact with wrong length phone (caught by validator)."""
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["add", "John", "123"])
            
        assert result.exit_code == 2
        output = result.output
        assert "Invalid value for 'PHONE'" in result.output
        mock_service.add_contact.assert_not_called()
    
    def test_add_contact_business_logic_error(self, mock_service):
        """Test adding contact with business logic error from service."""
        mock_service.add_contact.side_effect = ValueError("Phone already exists")
        
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["add", "John", "1234567890"])
            
        assert result.exit_code == 1
        assert "Error" in result.stdout
        assert "Phone already exists" in result.stdout


class TestChangeCommand:
    """Tests for change command."""
    
    def test_change_phone_success(self, mock_service):
        """Test changing phone successfully."""
        mock_service.change_contact.return_value = "Contact updated."
        
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["change", "John", "0123456789", "0987654321"])
            
        assert result.exit_code == 0
        assert "Contact updated" in result.stdout
        mock_service.change_contact.assert_called_once_with("John", "+380123456789", "+380987654321")
        mock_service.address_book.save_to_file.assert_called_once()
    
    def test_change_phone_invalid_old_phone_format(self, mock_service):
        """Test changing phone with invalid old phone format (caught by validator)."""
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["change", "John", "invalid", "0987654321"])
            
        assert result.exit_code == 2
        assert "Invalid phone number" in result.output
        mock_service.change_contact.assert_not_called()
    
    def test_change_phone_invalid_new_phone_format(self, mock_service):
        """Test changing phone with invalid new phone format (caught by validator)."""
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["change", "John", "1234567890", "123"])
            
        assert result.exit_code == 2
        assert "Phone number is not possible: 123" in result.output
        mock_service.change_contact.assert_not_called()
    
    def test_change_phone_contact_not_found(self, mock_service):
        """Test changing phone for non-existent contact."""
        mock_service.change_contact.side_effect = ValueError("Contact 'John' not found.")
        
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["change", "John", "1234567890", "0987654321"])
            
        assert result.exit_code == 1
        assert "Error" in result.stdout


class TestPhoneCommand:
    """Tests for phone command."""
    
    def test_phone_success(self, mock_service):
        """Test getting phone for existing contact."""
        mock_service.get_phone.return_value = "1234567890"
        
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["phone", "John"])
            
        assert result.exit_code == 0
        assert "1234567890" in result.stdout
        mock_service.get_phone.assert_called_once_with("John")
    
    def test_phone_contact_not_found(self, mock_service):
        """Test getting phone for non-existent contact."""
        mock_service.get_phone.side_effect = ValueError("Contact 'John' not found.")
        
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["phone", "John"])
            
        assert result.exit_code == 1
        assert "Error" in result.stdout


class TestAllCommand:
    """Tests for all command."""
    
    def test_all_with_contacts(self, mock_service):
        """Test showing all contacts without sorting."""
        mock_service.has_contacts.return_value = True
        mock_service.get_all_contacts.return_value = "Contact name: John, phones: 1234567890"
        
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["all"])
            
        assert result.exit_code == 0
        assert "John" in result.stdout
        # important: default sort_by=None
        mock_service.get_all_contacts.assert_called_once_with(sort_by=None)
    
    def test_all_with_sort_by_name(self, mock_service):
        """Test showing all contacts with sort-by=name."""
        mock_service.has_contacts.return_value = True
        mock_service.get_all_contacts.return_value = "Contact name: John, phones: 1234567890"
        
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["all", "--sort-by", "name"])
            
        assert result.exit_code == 0
        assert "John" in result.stdout
        # Typer converts "name" -> ContactSortBy.NAME
        mock_service.get_all_contacts.assert_called_once_with(
            sort_by=ContactSortBy.NAME
        )
    
    def test_all_empty(self, mock_service):
        """Test showing all contacts when address book is empty."""
        mock_service.has_contacts.return_value = False
        
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["all"])
            
        assert result.exit_code == 0
        assert "Address book is empty." in result.stdout
        mock_service.get_all_contacts.assert_not_called()


class TestAddBirthdayCommand:
    """Tests for add-birthday command."""
    
    def test_add_birthday_success(self, mock_service):
        """Test adding birthday successfully."""
        mock_service.add_birthday.return_value = "Birthday added."
        
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["add-birthday", "John", "15.05.1990"])
            
        assert result.exit_code == 0
        assert "Birthday added" in result.stdout
        mock_service.add_birthday.assert_called_once_with("John", "15.05.1990")
        mock_service.address_book.save_to_file.assert_called_once()
    
    def test_add_birthday_invalid_format_caught_by_validator(self, mock_service):
        """Test adding birthday with invalid format (caught by validator)."""
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["add-birthday", "John", "invalid"])
            
        assert result.exit_code == 2
        output = result.output
        assert "Invalid value" in output or "Invalid date format" in output
        mock_service.add_birthday.assert_not_called()
    
    def test_add_birthday_invalid_date_caught_by_validator(self, mock_service):
        """Test adding birthday with invalid date (caught by validator)."""
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["add-birthday", "John", "32.13.2020"])
            
        assert result.exit_code == 2
        output = result.output
        assert "Invalid value" in output or "Invalid date format" in output
        mock_service.add_birthday.assert_not_called()
    
    def test_add_birthday_contact_not_found(self, mock_service):
        """Test adding birthday for non-existent contact (business logic error)."""
        mock_service.add_birthday.side_effect = ValueError("Contact 'John' not found.")
        
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["add-birthday", "John", "15.05.1990"])
            
        assert result.exit_code == 1
        assert "Error" in result.stdout
        assert "Contact 'John' not found" in result.stdout


class TestShowBirthdayCommand:
    """Tests for show-birthday command."""
    
    def test_show_birthday_success(self, mock_service):
        """Test showing birthday successfully."""
        mock_service.get_birthday.return_value = "15.05.1990"
        
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["show-birthday", "John"])
            
        assert result.exit_code == 0
        assert "15.05.1990" in result.stdout
        mock_service.get_birthday.assert_called_once_with("John")
    
    def test_show_birthday_not_set(self, mock_service):
        """Test showing birthday when not set."""
        mock_service.get_birthday.return_value = "No birthday set for contact 'John'."
        
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["show-birthday", "John"])
            
        assert result.exit_code == 0
        assert "No birthday set" in result.stdout


class TestBirthdaysCommand:
    """Tests for birthdays command."""
    
    def test_birthdays_with_upcoming(self, mock_service):
        """Test showing upcoming birthdays."""
        mock_service.get_upcoming_birthdays.return_value = "John: 15.05.2024"
        
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["birthdays"])
            
        assert result.exit_code == 0
        assert "John" in result.stdout
    
    def test_birthdays_none(self, mock_service):
        """Test showing birthdays when none upcoming."""
        mock_service.get_upcoming_birthdays.return_value = "No upcoming birthdays in the next week."
        
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["birthdays"])
            
        assert result.exit_code == 0
        assert "No upcoming birthdays" in result.stdout
