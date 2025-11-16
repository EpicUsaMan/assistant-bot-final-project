"""Integration tests for group commands."""

import pytest
from typer.testing import CliRunner
from unittest.mock import Mock
from src.main import app, container
from src.services.contact_service import ContactService

runner = CliRunner()

# Module-level setup
import src.main
src.main.auto_register_commands()


@pytest.fixture
def mock_service():
    """Create a mock contact service."""
    service = Mock(spec=ContactService)
    service.address_book = Mock()
    service.address_book.save_to_file = Mock()
    return service


class TestGroupCommands:
    """Integration tests for group commands."""
    
    def test_group_show_command(self, mock_service):
        """Test group show command."""
        # group show command calls list_groups() and get_current_group()
        mock_service.list_groups.return_value = [("work", 5)]
        mock_service.get_current_group.return_value = "work"
        
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["group", "show", "work"])
            
        assert result.exit_code == 0
        mock_service.list_groups.assert_called_once()
        mock_service.get_current_group.assert_called_once()
    
    def test_group_rename_command(self, mock_service):
        """Test group rename command."""
        mock_service.rename_group.return_value = "Group renamed successfully."
        
        with container.contact_service.override(mock_service):
            result = runner.invoke(app, ["group", "rename", "old", "new"])
            
        assert result.exit_code == 0
        mock_service.rename_group.assert_called_once_with("old", "new")
        mock_service.address_book.save_to_file.assert_called_once()

