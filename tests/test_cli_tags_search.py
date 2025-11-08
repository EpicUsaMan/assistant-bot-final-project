"""
CLI tests for tag search (AND/OR) with CSV + quoted tokens.
Same style as other CLI tests (mocked service).
"""

import src.main
src.main.auto_register_commands()

from typer.testing import CliRunner
from unittest.mock import Mock
import pytest
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
    return svc


class TestFindByTags:
    def test_find_by_tags_and(self, mock_service):
        mock_service.find_by_tags_all.return_value = [
            ("Pavlo", Mock(tags_list=lambda: ["ml", "data,science"]))
        ]
        with container.contact_service.override(mock_service):
            r = runner.invoke(app, ["find-by-tags", 'ml,"data,science"'])
        assert r.exit_code == 0, r.output
        out = r.stdout.lower()
        assert "pavlo" in out and "data,science" in out
        mock_service.find_by_tags_all.assert_called_once_with(["ml", "data,science"])

    def test_find_by_tags_any_with_quoted(self, mock_service):
        mock_service.find_by_tags_any.return_value = [
            ("Alice", Mock(tags_list=lambda: ["ai"])),
            ("Bob",   Mock(tags_list=lambda: ["data,science"])),
        ]
        with container.contact_service.override(mock_service):
            r = runner.invoke(app, ["find-by-tags-any", '"data,science",ai'])
        assert r.exit_code == 0, r.output
        out = r.stdout.lower()
        assert "alice" in out and "bob" in out
        mock_service.find_by_tags_any.assert_called_once_with(["data,science", "ai"])
