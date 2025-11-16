"""Tests for edit commands (contact edit, contact phone edit, contact birthday edit)."""

import pytest
from typer.testing import CliRunner
from unittest.mock import Mock
from src.main import app, container
from src.models.address_book import AddressBook
from src.models.record import Record
from src.services.contact_service import ContactService

runner = CliRunner()

# Module-level setup
import src.main
src.main.auto_register_commands()


@pytest.fixture
def mock_service():
    """Create a mock contact service."""
    service = Mock(spec=ContactService)
    service.address_book = Mock(spec=AddressBook)
    service.address_book.save_to_file = Mock()
    return service


class TestContactEditCommand:
    """Tests for contact edit command."""
    
    def test_edit_contact_success(self, mock_service):
        """Test editing contact name successfully."""
        mock_service.edit_contact_name.return_value = "Contact renamed from 'John' to 'John Smith'."
        
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["contact", "edit", "John", "John Smith"])
            
        assert result.exit_code == 0
        assert "renamed" in result.stdout.lower()
        mock_service.edit_contact_name.assert_called_once_with("John", "John Smith")
        mock_service.address_book.save_to_file.assert_called_once()
    
    def test_edit_contact_not_found(self, mock_service):
        """Test editing non-existent contact."""
        mock_service.edit_contact_name.side_effect = ValueError("Contact 'John' not found.")
        
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["contact", "edit", "John", "John Smith"])
            
        # Error handler converts exception to exit code 1
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()


class TestContactPhoneEditCommand:
    """Tests for contact phone edit command."""
    
    def test_phone_edit_success(self, mock_service):
        """Test editing phone number successfully."""
        mock_service.change_contact.return_value = "Phone number updated."
        
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["contact", "phone", "edit", "John", "1234567890", "9876543210"])
            
        assert result.exit_code == 0
        assert "updated" in result.stdout.lower()
        # Phone numbers are formatted with country code
        mock_service.change_contact.assert_called_once_with("John", "+3801234567890", "+3809876543210")
        mock_service.address_book.save_to_file.assert_called_once()


class TestContactBirthdayEditCommand:
    """Tests for contact birthday edit command."""
    
    def test_birthday_edit_success(self, mock_service):
        """Test editing birthday successfully."""
        mock_service.add_birthday.return_value = "Birthday updated."
        
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["contact", "birthday", "edit", "John", "15.05.1990"])
            
        assert result.exit_code == 0
        assert "updated" in result.stdout.lower() or "added" in result.stdout.lower()
        mock_service.add_birthday.assert_called_once_with("John", "15.05.1990")
        mock_service.address_book.save_to_file.assert_called_once()

