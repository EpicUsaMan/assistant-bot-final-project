"""Tests for the AddressBook class."""

import pytest
from src.models.address_book import AddressBook
from src.models.record import Record


def test_address_book_initialization():
    """Test that AddressBook initializes as empty."""
    book = AddressBook()
    assert len(book.data) == 0


def test_address_book_add_record():
    """Test that AddressBook can add a record."""
    book = AddressBook()
    record = Record("John")
    book.add_record(record)
    assert len(book.data) == 1
    assert "John" in book.data


def test_address_book_add_multiple_records():
    """Test that AddressBook can add multiple records."""
    book = AddressBook()
    john_record = Record("John")
    jane_record = Record("Jane")
    book.add_record(john_record)
    book.add_record(jane_record)
    assert len(book.data) == 2


def test_address_book_add_duplicate_record_raises_error():
    """Test that adding duplicate record raises ValueError."""
    book = AddressBook()
    record1 = Record("John")
    record2 = Record("John")
    book.add_record(record1)
    with pytest.raises(ValueError, match="Record with name John already exists"):
        book.add_record(record2)


def test_address_book_find_record():
    """Test that AddressBook can find a record by name."""
    book = AddressBook()
    record = Record("John")
    book.add_record(record)
    found_record = book.find("John")
    assert found_record is not None
    assert found_record.name.value == "John"


def test_address_book_find_non_existent_record():
    """Test that finding non-existent record returns None."""
    book = AddressBook()
    found_record = book.find("John")
    assert found_record is None


def test_address_book_delete_record():
    """Test that AddressBook can delete a record."""
    book = AddressBook()
    record = Record("John")
    book.add_record(record)
    book.delete("John")
    assert len(book.data) == 0


def test_address_book_delete_non_existent_record_raises_error():
    """Test that deleting non-existent record raises KeyError."""
    book = AddressBook()
    with pytest.raises(KeyError, match="Record with name John not found"):
        book.delete("John")


def test_address_book_str_representation_empty():
    """Test that empty AddressBook returns correct string representation."""
    book = AddressBook()
    assert str(book) == "Address book is empty"


def test_address_book_str_representation_with_records():
    """Test that AddressBook with records returns correct string representation."""
    book = AddressBook()
    john_record = Record("John")
    john_record.add_phone("0123456789")
    book.add_record(john_record)
    jane_record = Record("Jane")
    jane_record.add_phone("0987654321")
    book.add_record(jane_record)
    
    result = str(book)
    assert "Contact name: John, phones: +380 123456789" in result
    assert "Contact name: Jane, phones: +380 98 765 4321" in result


def test_address_book_repr_representation():
    """Test that AddressBook returns correct repr representation."""
    book = AddressBook()
    record = Record("John")
    book.add_record(record)
    assert repr(book) == "AddressBook(records=1)"


def test_address_book_iteration():
    """Test that AddressBook can be iterated over."""
    book = AddressBook()
    john_record = Record("John")
    jane_record = Record("Jane")
    book.add_record(john_record)
    book.add_record(jane_record)
    
    names = [name for name in book.data.keys()]
    assert "John" in names
    assert "Jane" in names


def test_address_book_userdict_functionality():
    """Test that AddressBook inherits UserDict functionality."""
    book = AddressBook()
    record = Record("John")
    book.add_record(record)
    
    assert book["John"] == record
    assert len(book) == 1

