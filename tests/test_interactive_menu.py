"""Tests for interactive_menu module."""

import pytest
from unittest.mock import Mock, patch

from src.utils.interactive_menu import (
    MenuRegistry,
    get_menu_registry,
    register_menu,
    auto_menu,
    menu_command_map,
)


class TestMenuRegistry:
    """Tests for MenuRegistry class."""
    
    def test_init_creates_empty_registry(self):
        """Test initialization creates empty registry."""
        registry = MenuRegistry()
        assert registry._command_groups == {}
    
    def test_register_command_group(self):
        """Test registering a command group."""
        registry = MenuRegistry()
        commands = {
            "add": (lambda: None, "Add item"),
            "list": (lambda: None, "List items")
        }
        
        registry.register_command_group("test", commands)
        
        assert registry.has_group("test")
        assert registry.get_command_group("test") == commands
    
    def test_get_command_group_not_found(self):
        """Test getting non-existent command group returns None."""
        registry = MenuRegistry()
        assert registry.get_command_group("nonexistent") is None
    
    def test_has_group_false_for_nonexistent(self):
        """Test has_group returns False for non-existent group."""
        registry = MenuRegistry()
        assert registry.has_group("nonexistent") is False
    
    def test_has_group_true_for_existing(self):
        """Test has_group returns True for existing group."""
        registry = MenuRegistry()
        commands = {"add": (lambda: None, "Add item")}
        registry.register_command_group("test", commands)
        
        assert registry.has_group("test") is True


class TestGetMenuRegistry:
    """Tests for get_menu_registry function."""
    
    def test_returns_global_registry(self):
        """Test returns the global registry instance."""
        registry1 = get_menu_registry()
        registry2 = get_menu_registry()
        
        # Should return same instance
        assert registry1 is registry2


class TestRegisterMenuDecorator:
    """Tests for register_menu decorator."""
    
    def test_decorator_registers_commands(self):
        """Test decorator registers commands in global registry."""
        commands = {"add": (lambda: None, "Add item")}
        
        @register_menu("test_group", commands)
        def test_callback():
            pass
        
        registry = get_menu_registry()
        assert registry.has_group("test_group")
        assert registry.get_command_group("test_group") == commands
    
    def test_decorator_returns_original_function(self):
        """Test decorator returns original function."""
        def original_func():
            return "test"
        
        decorated = register_menu("test", {})(original_func)
        
        assert decorated is original_func
        assert decorated() == "test"


class TestMenuCommandMap:
    """Tests for menu_command_map helper."""
    
    def test_creates_command_map(self):
        """Test creates proper command map structure."""
        def add_func():
            pass
        
        def list_func():
            pass
        
        command_map = menu_command_map(
            ("add", add_func, "Add item", (None,)),
            ("list", list_func, "List items", ())
        )
        
        assert "add" in command_map
        assert "list" in command_map
        assert command_map["add"] == (add_func, "Add item", (None,))
        assert command_map["list"] == (list_func, "List items", ())
    
    def test_creates_empty_map(self):
        """Test creates empty map when no commands provided."""
        command_map = menu_command_map()
        assert command_map == {}


class TestAutoMenu:
    """Tests for auto_menu function."""
    
    @patch('src.utils.interactive_menu.questionary.select')
    def test_auto_menu_exits_on_exit_selection(self, mock_select):
        """Test auto_menu exits when user selects Exit."""
        mock_select.return_value.ask.return_value = "Exit"
        
        commands = menu_command_map(
            ("add", lambda: None, "Add item", ())
        )
        
        auto_menu(None, title="Test Menu", commands=commands)
        
        mock_select.assert_called_once()
    
    @patch('src.utils.interactive_menu.questionary.select')
    def test_auto_menu_exits_on_none(self, mock_select):
        """Test auto_menu exits when user cancels (None)."""
        mock_select.return_value.ask.return_value = None
        
        commands = menu_command_map(
            ("add", lambda: None, "Add item", ())
        )
        
        auto_menu(None, title="Test Menu", commands=commands)
        
        mock_select.assert_called_once()
    
    @patch('src.utils.interactive_menu.questionary.select')
    def test_auto_menu_calls_command(self, mock_select):
        """Test auto_menu calls selected command."""
        mock_func = Mock()
        
        # First call selects command, second call selects Exit
        mock_select.return_value.ask.side_effect = ["Add item", "Exit"]
        
        commands = menu_command_map(
            ("add", mock_func, "Add item", ())
        )
        
        auto_menu(None, title="Test Menu", commands=commands)
        
        mock_func.assert_called_once()
    
    @patch('src.utils.interactive_menu.questionary.select')
    def test_auto_menu_calls_command_with_args(self, mock_select):
        """Test auto_menu calls command with arguments."""
        mock_func = Mock()
        
        # First call selects command, second call selects Exit
        mock_select.return_value.ask.side_effect = ["Add item", "Exit"]
        
        commands = menu_command_map(
            ("add", mock_func, "Add item", (None, None))
        )
        
        auto_menu(None, title="Test Menu", commands=commands)
        
        mock_func.assert_called_once_with(None, None)
    
    @patch('src.utils.interactive_menu.questionary.select')
    def test_auto_menu_loops_until_exit(self, mock_select):
        """Test auto_menu loops until Exit is selected."""
        mock_func1 = Mock()
        mock_func2 = Mock()
        
        # Select commands twice, then exit
        mock_select.return_value.ask.side_effect = [
            "Add item",
            "List items",
            "Exit"
        ]
        
        commands = menu_command_map(
            ("add", mock_func1, "Add item", ()),
            ("list", mock_func2, "List items", ())
        )
        
        auto_menu(None, title="Test Menu", commands=commands)
        
        mock_func1.assert_called_once()
        mock_func2.assert_called_once()
    
    def test_auto_menu_no_commands_error(self):
        """Test auto_menu shows error when no commands."""
        auto_menu(None, title="Test Menu", commands=None)
        # Should print error and return without raising
    
    def test_auto_menu_with_group_name_not_found(self):
        """Test auto_menu shows error when group not found in registry."""
        auto_menu(None, group_name="nonexistent")
        # Should print error and return without raising
    
    def test_auto_menu_default_title(self):
        """Test auto_menu uses default title when not provided."""
        commands = menu_command_map(
            ("add", lambda: None, "Add item", ())
        )
        
        with patch('src.utils.interactive_menu.questionary.select') as mock_select:
            mock_select.return_value.ask.return_value = "Exit"
            auto_menu(None, group_name="test", commands=commands)
    
    def test_auto_menu_from_registry(self):
        """Test auto_menu loads commands from registry."""
        # Register commands in global registry
        registry = get_menu_registry()
        mock_func = Mock()
        commands = menu_command_map(
            ("add", mock_func, "Add item", ())
        )
        registry.register_command_group("test_registry", commands)
        
        with patch('src.utils.interactive_menu.questionary.select') as mock_select:
            # First call selects command, second call selects Exit
            mock_select.return_value.ask.side_effect = ["Add item", "Exit"]
            
            auto_menu(None, group_name="test_registry")
        
        mock_func.assert_called_once()
    
    def test_auto_menu_empty_commands_dict(self):
        """Test auto_menu with empty commands dictionary."""
        auto_menu(None, title="Empty Menu", commands={})
        # Should print error and return without raising


class TestAutoMenuIntegration:
    """Integration tests for auto_menu with real-world scenarios."""
    
    @patch('src.utils.interactive_menu.questionary.select')
    def test_notes_menu_simulation(self, mock_select):
        """Test simulating a notes menu."""
        add_note = Mock()
        list_notes = Mock()
        edit_note = Mock()
        
        # Simulate user flow: add -> list -> edit -> exit
        mock_select.return_value.ask.side_effect = [
            "Add note",
            "List notes",
            "Edit note",
            "Exit"
        ]
        
        commands = menu_command_map(
            ("add", add_note, "Add note", (None, None, None)),
            ("list", list_notes, "List notes", (None,)),
            ("edit", edit_note, "Edit note", (None, None, None)),
        )
        
        auto_menu(None, title="Notes Menu", commands=commands)
        
        add_note.assert_called_once_with(None, None, None)
        list_notes.assert_called_once_with(None)
        edit_note.assert_called_once_with(None, None, None)
    
    @patch('src.utils.interactive_menu.questionary.select')
    def test_submenu_navigation(self, mock_select):
        """Test submenu navigation."""
        main_menu_func = Mock()
        submenu_func = Mock()
        
        # User selects main option, then exits
        mock_select.return_value.ask.side_effect = ["Main option", "Exit"]
        
        # Main menu calls submenu
        def main_option():
            main_menu_func()
            # Simulate submenu
            submenu_commands = menu_command_map(
                ("sub", submenu_func, "Submenu option", ())
            )
            # In real scenario, this would call auto_menu again
        
        commands = menu_command_map(
            ("main", main_option, "Main option", ())
        )
        
        auto_menu(None, title="Main Menu", commands=commands)
        
        main_menu_func.assert_called_once()

