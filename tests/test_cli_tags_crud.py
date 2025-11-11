"""
CLI tests for Tags: add/remove/clear/list.
Style identical to tests/test_commands.py (mocked service + DI override).
"""

import src.main
src.main.auto_register_commands()

import pytest
from typer.testing import CliRunner
from unittest.mock import Mock
from src.main import app, container
from src.services.contact_service import ContactService

runner = CliRunner()


@pytest.fixture(autouse=True)
def setup_container():
    container.config.storage.filename.from_value("test_addressbook.pkl")
    yield


@pytest.fixture
def mock_service():
    svc = Mock(spec=ContactService)
    # mock persistence for @auto_save decorator
    svc.address_book = Mock()
    svc.address_book.save_to_file = Mock()
    return svc


class TestTagsCRUD:
    def test_tag_add_single(self, mock_service):
        mock_service.add_tag.return_value = "Tag 'ml' added to Pavlo."
        with container.contact_service.override(mock_service):
            r = runner.invoke(app, ["tag-add", "Pavlo", "ml"])
        assert r.exit_code == 0
        assert "added" in r.stdout.lower()
        mock_service.add_tag.assert_called_once_with("Pavlo", "ml")
        mock_service.address_book.save_to_file.assert_called_once()

    def test_tag_add_multiple_csv_with_quotes(self, mock_service):
        # input: one plain tag + one quoted CSV tag -> two calls expected
        mock_service.add_tag.side_effect = [
            "Tag 'ml' added to Pavlo.",
            "Tag 'data,science' added to Pavlo.",
        ]
        with container.contact_service.override(mock_service):
            r = runner.invoke(app, ["tag-add", "Pavlo", "ml", '"data,science"'])
        assert r.exit_code == 0, r.output
        out = r.stdout.lower()
        assert "ml" in out and "data,science" in out
        assert mock_service.add_tag.call_count == 2
        mock_service.add_tag.assert_any_call("Pavlo", "ml")
        mock_service.add_tag.assert_any_call("Pavlo", "data,science")
        mock_service.address_book.save_to_file.assert_called()

    def test_tag_list(self, mock_service):
        mock_service.list_tags.return_value = ["ml", "data,science"]
        with container.contact_service.override(mock_service):
            r = runner.invoke(app, ["tag-list", "Pavlo"])
        assert r.exit_code == 0
        assert "ml" in r.stdout and "data,science" in r.stdout
        mock_service.list_tags.assert_called_once_with("Pavlo")

    def test_tag_remove(self, mock_service):
        mock_service.remove_tag.return_value = "Tag 'ml' removed from Pavlo."
        with container.contact_service.override(mock_service):
            r = runner.invoke(app, ["tag-remove", "Pavlo", "ml"])
        assert r.exit_code == 0
        assert "removed" in r.stdout.lower()
        mock_service.remove_tag.assert_called_once_with("Pavlo", "ml")
        mock_service.address_book.save_to_file.assert_called_once()

    def test_tag_clear(self, mock_service):
        mock_service.clear_tags.return_value = "All tags cleared for Pavlo."
        with container.contact_service.override(mock_service):
            r = runner.invoke(app, ["tag-clear", "Pavlo"])
        assert r.exit_code == 0
        assert "cleared" in r.stdout.lower()
        mock_service.clear_tags.assert_called_once_with("Pavlo")
        mock_service.address_book.save_to_file.assert_called_once()
