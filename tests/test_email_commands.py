"""Tests for email commands module."""

import src.main
src.main.auto_register_commands()

import pytest
from unittest.mock import Mock, patch
from typer.testing import CliRunner
import click

from src.commands.contact import (
    email_app as app,
    _email_add_impl as _add_email_impl,
    _email_remove_impl as _remove_email_impl,
)
from src.main import app as main_app, container

runner = CliRunner()


@pytest.fixture
def mock_contact_service():
    """Create a mock contact service."""
    service = Mock()
    service.has_contacts.return_value = True
    service.list_contacts.return_value = [("John", Mock())]
    service.address_book = Mock()
    service.address_book.save_to_file = Mock()
    return service


class TestAddEmailImpl:
    """Tests for _add_email_impl function."""
    
    def test_add_email_success(self, mock_contact_service):
        """Test adding an email successfully."""
        mock_contact_service.add_email.return_value = "Email added to John."
        
        _add_email_impl("John", "john@example.com", service=mock_contact_service, filename="test.pkl")
        
        mock_contact_service.add_email.assert_called_once_with("John", "john@example.com")
        mock_contact_service.address_book.save_to_file.assert_called_once()
    
    def test_add_email_updates_existing(self, mock_contact_service):
        """Test that adding email updates existing email."""
        mock_contact_service.add_email.return_value = "Email added to John."
        
        _add_email_impl("John", "john.new@example.com", service=mock_contact_service, filename="test.pkl")
        
        mock_contact_service.add_email.assert_called_once_with("John", "john.new@example.com")


class TestRemoveEmailImpl:
    """Tests for _remove_email_impl function."""
    
    def test_remove_email_success(self, mock_contact_service):
        """Test removing an email successfully."""
        mock_contact_service.remove_email.return_value = "Email removed from John."
        
        _remove_email_impl("John", service=mock_contact_service, filename="test.pkl")
        
        mock_contact_service.remove_email.assert_called_once_with("John")
        mock_contact_service.address_book.save_to_file.assert_called_once()
    
    def test_remove_email_not_set(self, mock_contact_service):
        """Test removing email when not set."""
        mock_contact_service.remove_email.return_value = "No email set for contact 'John'."
        
        _remove_email_impl("John", service=mock_contact_service, filename="test.pkl")
        
        mock_contact_service.remove_email.assert_called_once_with("John")


class TestEmailCommandsCLI:
    """Tests for email CLI commands using CliRunner."""
    
    @pytest.fixture(autouse=True)
    def setup_container(self):
        """Set up the DI container before each test."""
        container.config.storage.filename.from_value("test_addressbook.pkl")
        yield
    
    def test_email_add_success(self, mock_contact_service):
        """Test email add command successfully."""
        mock_contact_service.add_email.return_value = "Email added to John."
        
        with container.contact_service.override(mock_contact_service):
            result = runner.invoke(app, ["add", "John", "john@example.com"])
        
        assert result.exit_code == 0
        assert "added" in result.stdout.lower()
        mock_contact_service.add_email.assert_called_once_with("John", "john@example.com")
        mock_contact_service.address_book.save_to_file.assert_called_once()
    
    def test_email_add_invalid_format_caught_by_validator(self, mock_contact_service):
        """Test email add with invalid format (caught by validator)."""
        with container.contact_service.override(mock_contact_service):
            result = runner.invoke(app, ["add", "John", "invalid-email"])
        
        assert result.exit_code == 2
        output = result.output
        assert "invalid" in output.lower() or "email" in output.lower()
        mock_contact_service.add_email.assert_not_called()
    
    def test_email_add_contact_not_found(self, mock_contact_service):
        """Test email add for non-existent contact (business logic error)."""
        mock_contact_service.add_email.side_effect = ValueError("Contact 'John' not found.")
        
        with container.contact_service.override(mock_contact_service):
            result = runner.invoke(app, ["add", "John", "john@example.com"])
        
        assert result.exit_code == 1
        assert "Error" in result.stdout or "not found" in result.stdout.lower()
    
    def test_email_remove_success(self, mock_contact_service):
        """Test email remove command successfully."""
        mock_contact_service.remove_email.return_value = "Email removed from John."
        
        with container.contact_service.override(mock_contact_service):
            result = runner.invoke(app, ["remove", "John"])
        
        assert result.exit_code == 0
        assert "removed" in result.stdout.lower()
        mock_contact_service.remove_email.assert_called_once_with("John")
        mock_contact_service.address_book.save_to_file.assert_called_once()
    
    def test_email_remove_contact_not_found(self, mock_contact_service):
        """Test email remove for non-existent contact."""
        mock_contact_service.remove_email.side_effect = ValueError("Contact 'John' not found.")
        
        with container.contact_service.override(mock_contact_service):
            result = runner.invoke(app, ["remove", "John"])
        
        assert result.exit_code == 1
        assert "Error" in result.stdout or "not found" in result.stdout.lower()
    
    def test_email_remove_not_set(self, mock_contact_service):
        """Test email remove when email is not set."""
        mock_contact_service.remove_email.return_value = "No email set for contact 'John'."
        
        with container.contact_service.override(mock_contact_service):
            result = runner.invoke(app, ["remove", "John"])
        
        assert result.exit_code == 0
        assert "No email set" in result.stdout
    
    def test_email_add_via_main_app(self, mock_contact_service):
        """Test email add command via main app."""
        mock_contact_service.add_email.return_value = "Email added to John."
        
        with container.contact_service.override(mock_contact_service):
            result = runner.invoke(main_app, ["contact", "email", "add", "John", "john@example.com"])
        
        assert result.exit_code == 0
        assert "added" in result.stdout.lower()
        mock_contact_service.add_email.assert_called_once_with("John", "john@example.com")

