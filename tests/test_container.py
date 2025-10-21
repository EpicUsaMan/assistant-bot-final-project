"""
Tests for the DI container.

This module tests that the dependency injection container is properly configured.
"""

import pytest
from src.container import Container
from src.models.address_book import AddressBook
from src.services.contact_service import ContactService


@pytest.fixture
def container():
    """Create a container for testing."""
    container = Container()
    container.config.storage.filename.from_value("test_addressbook.pkl")
    return container


class TestContainerConfiguration:
    """Tests for container configuration."""
    
    def test_address_book_is_singleton(self, container):
        """Test that address book is a singleton."""
        book1 = container.address_book()
        book2 = container.address_book()
        assert book1 is book2
    
    def test_contact_service_is_factory(self, container):
        """Test that contact service is a factory."""
        service1 = container.contact_service()
        service2 = container.contact_service()
        # Factories create new instances, but they share the same address book
        assert isinstance(service1, ContactService)
        assert isinstance(service2, ContactService)
        # They should use the same address book instance
        assert service1.address_book is service2.address_book


class TestContainerProvides:
    """Tests for container providing correct instances."""
    
    def test_provides_address_book(self, container):
        """Test that container provides AddressBook."""
        book = container.address_book()
        assert isinstance(book, AddressBook)
    
    def test_provides_contact_service(self, container):
        """Test that container provides ContactService."""
        service = container.contact_service()
        assert isinstance(service, ContactService)
        assert isinstance(service.address_book, AddressBook)


class TestContainerSaveData:
    """Tests for container save_data method."""
    
    def test_save_data(self, container, tmp_path):
        """Test that save_data saves the address book."""
        # Update config to use temp file
        test_file = tmp_path / "test.pkl"
        container.config.storage.filename.from_value(str(test_file))
        
        # Add some data
        book = container.address_book()
        from src.models.record import Record
        record = Record("Test")
        record.add_phone("1234567890")
        book.add_record(record)
        
        # Save data - models handle their own serialization
        book.save_to_file(str(test_file))
        
        # Check file exists
        assert test_file.exists()
        
        # Load and verify
        loaded_book = AddressBook.load_from_file(str(test_file))
        assert loaded_book.find("Test") is not None

