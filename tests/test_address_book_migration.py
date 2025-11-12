# tests/test_address_book_migration.py
import pickle
from pathlib import Path

from src.models.address_book import AddressBook
from src.models.record import Record
from src.models.group import DEFAULT_GROUP_ID


def test_load_from_legacy_file_assigns_personal_group(tmp_path):
    """
    Legacy format:
    - keys w/o group prefix
    - no attributes groups/current_group_id
    """
    path = tmp_path / "legacy_addressbook.pkl"

    # create "old" book
    book = AddressBook()
    # old state imitatiotn
    if hasattr(book, "groups"):
        del book.groups
    if hasattr(book, "current_group_id"):
        del book.current_group_id

    # keys w/o prefix
    rec = Record("John")
    # old Record w/o group_id
    del rec.group_id
    book.data.clear()
    book.data["John"] = rec

    with path.open("wb") as fh:
        pickle.dump(book, fh)

    # load
    loaded = AddressBook.load_from_file(str(path))

    assert loaded.current_group_id == DEFAULT_GROUP_ID
    assert loaded.has_group(DEFAULT_GROUP_ID)

    key = f"{DEFAULT_GROUP_ID}:John"
    assert key in loaded.data

    rec2 = loaded.find("John")
    assert rec2 is not None
    assert rec2.group_id == DEFAULT_GROUP_ID


def test_load_from_nonexistent_file_returns_empty(tmp_path):
    path = tmp_path / "no_such_file.pkl"
    book = AddressBook.load_from_file(str(path))
    assert isinstance(book, AddressBook)
    assert len(book.data) == 0
