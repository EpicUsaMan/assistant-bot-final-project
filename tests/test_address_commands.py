"""Tests for address commands module."""

import src.main
src.main.auto_register_commands()

import pytest
from unittest.mock import Mock, patch
from typer.testing import CliRunner
import click

from src.commands.address import (
    app,
    _set_address_impl,
    _remove_address_impl,
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


class TestSetAddressImpl:
    """Tests for _set_address_impl function."""
    
    def test_set_address_success(self, mock_contact_service):
        """Test setting an address successfully."""
        mock_contact_service.set_address.return_value = "Address set for John."
        
        _set_address_impl("John", "UA", "Kyiv", "Main St 1", service=mock_contact_service, filename="test.pkl")
        
        mock_contact_service.set_address.assert_called_once_with("John", "UA", "Kyiv", "Main St 1")
        mock_contact_service.address_book.save_to_file.assert_called_once()
    
    def test_set_address_updates_existing(self, mock_contact_service):
        """Test that setting address updates existing address."""
        mock_contact_service.set_address.return_value = "Address set for John."
        
        _set_address_impl("John", "PL", "Warsaw", "New St 2", service=mock_contact_service, filename="test.pkl")
        
        mock_contact_service.set_address.assert_called_once_with("John", "PL", "Warsaw", "New St 2")


class TestRemoveAddressImpl:
    """Tests for _remove_address_impl function."""
    
    def test_remove_address_success(self, mock_contact_service):
        """Test removing an address successfully."""
        mock_contact_service.remove_address.return_value = "Address removed from John."
        
        _remove_address_impl("John", service=mock_contact_service, filename="test.pkl")
        
        mock_contact_service.remove_address.assert_called_once_with("John")
        mock_contact_service.address_book.save_to_file.assert_called_once()
    
    def test_remove_address_not_set(self, mock_contact_service):
        """Test removing address when not set."""
        mock_contact_service.remove_address.return_value = "No address set for contact 'John'."
        
        _remove_address_impl("John", service=mock_contact_service, filename="test.pkl")
        
        mock_contact_service.remove_address.assert_called_once_with("John")


class TestAddressCommandsCLI:
    """Tests for address CLI commands using CliRunner."""
    
    @pytest.fixture(autouse=True)
    def setup_container(self):
        """Set up the DI container before each test."""
        container.config.storage.filename.from_value("test_addressbook.pkl")
        yield
    
    def test_address_set_success(self, mock_contact_service):
        """Test address set command successfully."""
        mock_contact_service.set_address.return_value = "Address set for John."
        
        with container.contact_service.override(mock_contact_service):
            result = runner.invoke(app, ["set", "John", "UA", "Kyiv", "Main St 1"])
        
        assert result.exit_code == 0
        assert "set" in result.stdout.lower()
        mock_contact_service.set_address.assert_called_once_with("John", "UA", "Kyiv", "Main St 1")
        mock_contact_service.address_book.save_to_file.assert_called_once()
    
    def test_address_set_contact_not_found(self, mock_contact_service):
        """Test address set for non-existent contact (business logic error)."""
        mock_contact_service.set_address.side_effect = ValueError("Contact 'John' not found.")
        
        with container.contact_service.override(mock_contact_service):
            result = runner.invoke(app, ["set", "John", "UA", "Kyiv", "Main St 1"])
        
        assert result.exit_code == 1
        assert "Error" in result.stdout or "not found" in result.stdout.lower()
    
    def test_address_remove_success(self, mock_contact_service):
        """Test address remove command successfully."""
        mock_contact_service.remove_address.return_value = "Address removed from John."
        
        with container.contact_service.override(mock_contact_service):
            result = runner.invoke(app, ["remove", "John"])
        
        assert result.exit_code == 0
        assert "removed" in result.stdout.lower()
        mock_contact_service.remove_address.assert_called_once_with("John")
        mock_contact_service.address_book.save_to_file.assert_called_once()
    
    def test_address_remove_contact_not_found(self, mock_contact_service):
        """Test address remove for non-existent contact."""
        mock_contact_service.remove_address.side_effect = ValueError("Contact 'John' not found.")
        
        with container.contact_service.override(mock_contact_service):
            result = runner.invoke(app, ["remove", "John"])
        
        assert result.exit_code == 1
        assert "Error" in result.stdout or "not found" in result.stdout.lower()
    
    def test_address_remove_not_set(self, mock_contact_service):
        """Test address remove when address is not set."""
        mock_contact_service.remove_address.return_value = "No address set for contact 'John'."
        
        with container.contact_service.override(mock_contact_service):
            result = runner.invoke(app, ["remove", "John"])
        
        assert result.exit_code == 0
        assert "No address set" in result.stdout
    
    def test_address_set_via_main_app(self, mock_contact_service):
        """Test address set command via main app."""
        mock_contact_service.set_address.return_value = "Address set for John."
        
        with container.contact_service.override(mock_contact_service):
            result = runner.invoke(main_app, ["address", "set", "John", "UA", "Kyiv", "Main St 1"])
        
        assert result.exit_code == 0
        assert "set" in result.stdout.lower()
        mock_contact_service.set_address.assert_called_once_with("John", "UA", "Kyiv", "Main St 1")

