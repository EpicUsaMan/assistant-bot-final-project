"""
CLI tests for Groups commands.
Style identical to test_cli_tags_crud.py.
"""

import src.main
src.main.auto_register_commands()

from typer.testing import CliRunner
from unittest.mock import Mock
from src.main import app, container
from src.services.contact_service import ContactService
import pytest

runner = CliRunner()


@pytest.fixture(autouse=True)
def setup_container():
    container.config.storage.filename.from_value("test_addressbook.pkl")
    yield


@pytest.fixture
def mock_service():
    svc = Mock(spec=ContactService)
    svc.address_book = Mock()
    svc.address_book.save_to_file = Mock()
    return svc


class TestGroupsCLI:
    def test_group_list_default(self, mock_service):
        mock_service.list_groups.return_value = [("personal", 0)]
        mock_service.get_current_group.return_value = "personal"

        with container.contact_service.override(mock_service):
            r = runner.invoke(app, ["group-list"])
        assert r.exit_code == 0
        assert "personal" in r.stdout

    def test_group_add_creates(self, mock_service):
        with container.contact_service.override(mock_service):
            r = runner.invoke(app, ["group-add", "work"])
        assert r.exit_code == 0
        assert "Group 'work' created" in r.stdout
        mock_service.add_group.assert_called_once_with("work")
        mock_service.address_book.save_to_file.assert_called_once()

    def test_group_use_switch_success(self, mock_service):
        with container.contact_service.override(mock_service):
            r = runner.invoke(app, ["group-use", "work"])
        assert r.exit_code == 0
        assert "Current group set to 'work'" in r.stdout
        mock_service.set_current_group.assert_called_once_with("work")
        mock_service.address_book.save_to_file.assert_called_once()

    def test_group_rename_uses_service(self, mock_service):
        mock_service.rename_group.return_value = "Group 'work' renamed to 'team'."

        with container.contact_service.override(mock_service):
            r = runner.invoke(app, ["group-rename", "work", "team"])

        assert r.exit_code == 0, r.stdout
        mock_service.rename_group.assert_called_once_with("work", "team")
        mock_service.address_book.save_to_file.assert_called_once()
        assert "renamed" in r.stdout.lower()

    def test_group_remove_without_force(self, mock_service):
        mock_service.remove_group.return_value = "Group 'work' removed."

        with container.contact_service.override(mock_service):
            r = runner.invoke(app, ["group-remove", "work"])

        assert r.exit_code == 0, r.stdout
        mock_service.remove_group.assert_called_once_with("work", force=False)
        mock_service.address_book.save_to_file.assert_called_once()
        assert "removed" in r.stdout.lower()

    def test_group_remove_with_force(self, mock_service):
        mock_service.remove_group.return_value = "Group 'work' and its contacts removed."

        with container.contact_service.override(mock_service):
            r = runner.invoke(app, ["group-remove", "work", "--force"])

        assert r.exit_code == 0, r.stdout
        mock_service.remove_group.assert_called_once_with("work", force=True)
        mock_service.address_book.save_to_file.assert_called_once()
        assert "contacts" in r.stdout.lower()