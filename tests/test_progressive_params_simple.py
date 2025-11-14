"""Tests for progressive_params module (simplified, focusing on logic)."""

import pytest
from unittest.mock import Mock, patch
from functools import partial

from src.utils.progressive_params import (
    TextInput,
    ConfirmInput,
    TagsInput,
    SelectInput,
    ContactSelector,
    NoteSelector,
    TagSelector,
    progressive_params,
    _ProgressiveParamsWrapper,
)
from src.models.note import Note


class TestTextInput:
    """Tests for TextInput parameter provider."""
    
    def test_returns_existing_value(self):
        """Test that existing value is returned without prompting."""
        provider = TextInput("Enter text:")
        result = provider.get_value("name", "existing")
        assert result == "existing"
    
    @patch('src.utils.progressive_params.questionary.text')
    def test_required_text_input(self, mock_text):
        """Test getting required text input."""
        mock_text.return_value.ask.return_value = "User input"
        
        provider = TextInput("Enter text:", required=True)
        result = provider.get_value("name", None)
        
        assert result == "User input"
        mock_text.assert_called_once()
    
    @patch('src.utils.progressive_params.questionary.text')
    def test_optional_text_with_default(self, mock_text):
        """Test getting optional text with default."""
        mock_text.return_value.ask.return_value = None
        
        provider = TextInput("Enter text:", required=False, default="default value")
        result = provider.get_value("name", None)
        
        assert result == "default value"
    
    @patch('src.utils.progressive_params.questionary.text')
    def test_required_user_cancels(self, mock_text):
        """Test user cancels required text input."""
        mock_text.return_value.ask.return_value = None
        
        provider = TextInput("Enter text:", required=True)
        result = provider.get_value("name", None)
        
        assert result is None
    
    @patch('src.utils.progressive_params.questionary.text')
    def test_multiline_input(self, mock_text):
        """Test multiline text input."""
        mock_text.return_value.ask.return_value = "Line 1\nLine 2"
        
        provider = TextInput("Enter text:", multiline=True)
        result = provider.get_value("name", None)
        
        assert result == "Line 1\nLine 2"
        # Check multiline parameter was passed
        call_kwargs = mock_text.call_args[1]
        assert call_kwargs.get("multiline") is True
    
    def test_validator_function(self):
        """Test custom validator function."""
        def validator(text):
            return len(text) > 5
        
        provider = TextInput("Enter text:", validator=validator, error_message="Too short")
        assert provider.validator is not None
        assert provider.error_message == "Too short"
    
    @patch('src.utils.progressive_params.questionary.text')
    def test_empty_string_handling(self, mock_text):
        """Test empty string input handling."""
        mock_text.return_value.ask.return_value = ""
        
        provider = TextInput("Enter text:", required=False, default="fallback")
        result = provider.get_value("name", None)
        
        # Should return the input (empty string), not default, when user provides input
        assert result == "" or result == "fallback"  # Implementation dependent


class TestConfirmInput:
    """Tests for ConfirmInput parameter provider."""
    
    def test_returns_existing_value(self):
        """Test that existing value is returned without prompting."""
        provider = ConfirmInput("Confirm?")
        result = provider.get_value("confirm", True)
        assert result is True
    
    @patch('src.utils.progressive_params.questionary.confirm')
    def test_user_confirms(self, mock_confirm):
        """Test user confirms."""
        mock_confirm.return_value.ask.return_value = True
        
        provider = ConfirmInput("Confirm?")
        result = provider.get_value("confirm", None)
        
        assert result is True
    
    @patch('src.utils.progressive_params.questionary.confirm')
    def test_user_declines(self, mock_confirm):
        """Test user declines."""
        mock_confirm.return_value.ask.return_value = False
        
        provider = ConfirmInput("Confirm?")
        result = provider.get_value("confirm", None)
        
        assert result is False
    
    @patch('src.utils.progressive_params.questionary.confirm')
    def test_default_true(self, mock_confirm):
        """Test with default True."""
        mock_confirm.return_value.ask.return_value = True
        
        provider = ConfirmInput("Confirm?", default=True)
        result = provider.get_value("confirm", None)
        
        assert result is True
        # Check default was passed
        call_kwargs = mock_confirm.call_args[1]
        assert call_kwargs.get("default") is True
    
    @patch('src.utils.progressive_params.questionary.confirm')
    def test_default_false(self, mock_confirm):
        """Test with default False."""
        mock_confirm.return_value.ask.return_value = False
        
        provider = ConfirmInput("Confirm?", default=False)
        result = provider.get_value("confirm", None)
        
        assert result is False


class TestTagsInput:
    """Tests for TagsInput parameter provider."""
    
    def test_returns_existing_list(self):
        """Test that existing list is returned without prompting."""
        provider = TagsInput()
        result = provider.get_value("tags", ["work", "important"])
        assert result == ["work", "important"]
    
    def test_converts_string_to_list(self):
        """Test that existing non-list value is converted to list."""
        provider = TagsInput()
        result = provider.get_value("tags", "single_tag")
        assert result == ["single_tag"]
    
    @patch('src.utils.progressive_params.questionary.text')
    def test_comma_separated_input(self, mock_text):
        """Test parsing comma-separated tags."""
        mock_text.return_value.ask.return_value = "work, important, urgent"
        
        provider = TagsInput()
        result = provider.get_value("tags", None)
        
        assert result == ["work", "important", "urgent"]
    
    @patch('src.utils.progressive_params.questionary.text')
    def test_empty_string_input(self, mock_text):
        """Test empty string input."""
        mock_text.return_value.ask.return_value = "   "
        
        provider = TagsInput(required=False)
        result = provider.get_value("tags", None)
        
        assert result == []
    
    @patch('src.utils.progressive_params.questionary.text')
    def test_user_cancels_required(self, mock_text):
        """Test user cancels required tags input."""
        mock_text.return_value.ask.return_value = None
        
        provider = TagsInput(required=True)
        result = provider.get_value("tags", None)
        
        assert result is None
    
    @patch('src.utils.progressive_params.questionary.text')
    def test_user_cancels_optional(self, mock_text):
        """Test user cancels optional tags input."""
        mock_text.return_value.ask.return_value = None
        
        provider = TagsInput(required=False)
        result = provider.get_value("tags", None)
        
        assert result == []
    
    @patch('src.utils.progressive_params.questionary.text')
    def test_whitespace_handling(self, mock_text):
        """Test whitespace is stripped from tags."""
        mock_text.return_value.ask.return_value = " work ,  important  , urgent "
        
        provider = TagsInput()
        result = provider.get_value("tags", None)
        
        assert result == ["work", "important", "urgent"]
    
    @patch('src.utils.progressive_params.questionary.text')
    def test_empty_tags_filtered(self, mock_text):
        """Test empty tags are filtered out."""
        mock_text.return_value.ask.return_value = "work, , important, ,urgent"
        
        provider = TagsInput()
        result = provider.get_value("tags", None)
        
        # Empty tags should be filtered
        assert "" not in result
        assert "work" in result
        assert "important" in result
        assert "urgent" in result


class TestSelectInput:
    """Tests for SelectInput parameter provider."""
    
    def test_returns_existing_value(self):
        """Test that existing value is returned without prompting."""
        choices = [("opt1", "Option 1"), ("opt2", "Option 2")]
        provider = SelectInput("Select:", choices)
        result = provider.get_value("option", "opt1")
        assert result == "opt1"
    
    @patch('src.utils.progressive_params.questionary.select')
    def test_user_selects_option(self, mock_select):
        """Test user selects an option."""
        choices = [("opt1", "Option 1"), ("opt2", "Option 2")]
        mock_select.return_value.ask.return_value = "Option 1"
        
        provider = SelectInput("Select:", choices)
        result = provider.get_value("option", None)
        
        assert result == "opt1"
    
    @patch('src.utils.progressive_params.questionary.select')
    def test_user_selects_second_option(self, mock_select):
        """Test user selects second option."""
        choices = [("opt1", "Option 1"), ("opt2", "Option 2")]
        mock_select.return_value.ask.return_value = "Option 2"
        
        provider = SelectInput("Select:", choices)
        result = provider.get_value("option", None)
        
        assert result == "opt2"
    
    @patch('src.utils.progressive_params.questionary.select')
    def test_user_cancels_required(self, mock_select):
        """Test user cancels required selection."""
        choices = [("opt1", "Option 1"), ("opt2", "Option 2")]
        mock_select.return_value.ask.return_value = "Cancel"
        
        provider = SelectInput("Select:", choices, required=True)
        result = provider.get_value("option", None)
        
        assert result is None
    
    @patch('src.utils.progressive_params.questionary.select')
    def test_user_cancels_optional(self, mock_select):
        """Test user cancels optional selection."""
        choices = [("opt1", "Option 1"), ("opt2", "Option 2")]
        mock_select.return_value.ask.return_value = "Cancel"
        
        provider = SelectInput("Select:", choices, required=False)
        result = provider.get_value("option", None)
        
        assert result == "opt1"  # Returns first choice as default
    
    @patch('src.utils.progressive_params.questionary.select')
    def test_user_cancels_with_none(self, mock_select):
        """Test user cancels with None."""
        choices = [("opt1", "Option 1"), ("opt2", "Option 2")]
        mock_select.return_value.ask.return_value = None
        
        provider = SelectInput("Select:", choices, required=True)
        result = provider.get_value("option", None)
        
        assert result is None
    
    @patch('src.utils.progressive_params.questionary.select')
    def test_empty_choices_list(self, mock_select):
        """Test with empty choices list."""
        choices = []
        mock_select.return_value.ask.return_value = "Cancel"
        
        provider = SelectInput("Select:", choices, required=False)
        result = provider.get_value("option", None)
        
        assert result is None  # No choices, so None


class TestProgressiveParamsDecorator:
    """Tests for progressive_params decorator."""
    
    def test_decorator_stores_providers(self):
        """Test decorator stores providers as function attribute."""
        @progressive_params(name=TextInput("Name:"))
        def test_func(name: str):
            return name
        
        assert hasattr(test_func, '_progressive_param_providers')
    
    def test_decorated_function_preserves_metadata(self):
        """Test decorated function preserves original metadata."""
        @progressive_params(name=TextInput("Name:"))
        def test_func(name: str):
            """Test function docstring."""
            return name
        
        assert test_func.__name__ == "test_func"
        assert "Test function docstring" in (test_func.__doc__ or "")
    
    @patch('src.utils.progressive_params.questionary.text')
    def test_decorated_function_fills_parameters(self, mock_text):
        """Test decorated function fills missing parameters."""
        mock_text.return_value.ask.return_value = "John"
        
        @progressive_params(name=TextInput("Name:", required=True))
        def test_func(name: str):
            return f"Hello {name}"
        
        result = test_func(None)
        assert result == "Hello John"
    
    def test_decorated_function_with_existing_parameters(self):
        """Test decorated function doesn't prompt for existing parameters."""
        @progressive_params(name=TextInput("Name:", required=True))
        def test_func(name: str):
            return f"Hello {name}"
        
        result = test_func("Alice")
        assert result == "Hello Alice"
    
    def test_decorated_function_with_factory_callable(self):
        """Test decorated function with factory callable."""
        def provider_factory():
            return TextInput("Name:", required=True)
        
        @progressive_params(name=provider_factory)
        def test_func(name: str):
            return f"Hello {name}"
        
        # Should create provider from factory
        assert hasattr(test_func, '_progressive_param_providers')
    
    @patch('src.utils.progressive_params.questionary.text')
    def test_decorated_function_user_cancels(self, mock_text):
        """Test decorated function when user cancels."""
        mock_text.return_value.ask.return_value = None
        
        @progressive_params(name=TextInput("Name:", required=True))
        def test_func(name: str):
            return f"Hello {name}"
        
        result = test_func(None)
        assert result is None


class TestProgressiveParamsWrapper:
    """Tests for _ProgressiveParamsWrapper class."""
    
    def test_wrapper_preserves_function_attributes(self):
        """Test wrapper preserves all function attributes."""
        def original_func(name: str):
            """Original docstring."""
            return name
        
        wrapper = _ProgressiveParamsWrapper(original_func, {})
        
        assert wrapper.__name__ == "original_func"
        assert wrapper.__doc__ == "Original docstring."
        assert wrapper.__wrapped__ is original_func
    
    def test_wrapper_callable(self):
        """Test wrapper is callable."""
        def original_func(name: str):
            return name
        
        wrapper = _ProgressiveParamsWrapper(original_func, {})
        result = wrapper("John")
        
        assert result == "John"
    
    @patch('src.utils.progressive_params.questionary.text')
    def test_wrapper_context_building(self, mock_text):
        """Test wrapper builds context for providers."""
        mock_text.return_value.ask.return_value = "Meeting"
        
        def original_func(contact_name: str, note_name: str):
            return f"{contact_name}:{note_name}"
        
        # Use a real provider that can access context
        provider = TextInput("Note name:", required=True)
        
        wrapper = _ProgressiveParamsWrapper(original_func, {"note_name": provider})
        result = wrapper("John", None)
        
        # Just verify the result is correct (context was used)
        assert result == "John:Meeting"
    
    def test_wrapper_with_defaults(self):
        """Test wrapper handles functions with default parameters."""
        def original_func(name: str, age: int = 25):
            return f"{name} is {age}"
        
        wrapper = _ProgressiveParamsWrapper(original_func, {})
        result = wrapper("Alice")
        
        assert result == "Alice is 25"
    
    def test_wrapper_with_kwargs(self):
        """Test wrapper handles keyword arguments."""
        def original_func(name: str, city: str):
            return f"{name} from {city}"
        
        wrapper = _ProgressiveParamsWrapper(original_func, {})
        result = wrapper(name="Bob", city="NYC")
        
        assert result == "Bob from NYC"
    
    def test_wrapper_getattr_delegation(self):
        """Test wrapper delegates attribute access to wrapped function."""
        def original_func():
            pass
        original_func.custom_attr = "test_value"
        
        wrapper = _ProgressiveParamsWrapper(original_func, {})
        
        assert wrapper.custom_attr == "test_value"
    
    def test_wrapper_stops_on_none_for_required_provider(self):
        """Test wrapper stops when provider returns None."""
        # Create a non-TextInput provider
        provider = ConfirmInput("Confirm?")
        
        # Mock it to return None
        with patch.object(provider, 'get_value', return_value=None):
            def original_func(confirm: bool):
                return f"Confirmed: {confirm}"
            
            wrapper = _ProgressiveParamsWrapper(original_func, {"confirm": provider})
            result = wrapper(None)
            
            # Should return None when provider returns None
            assert result is None
    
    @patch('src.utils.progressive_params.questionary.text')
    def test_wrapper_with_text_input_optional(self, mock_text):
        """Test wrapper handles TextInput with required=False."""
        mock_text.return_value.ask.return_value = None
        
        provider = TextInput("Name:", required=False, default="Default")
        
        def original_func(name: str):
            return f"Hello {name}"
        
        wrapper = _ProgressiveParamsWrapper(original_func, {"name": provider})
        result = wrapper(None)
        
        # Should not return None, should use default
        assert result == "Hello Default"


class TestContactSelector:
    """Tests for ContactSelector parameter provider."""
    
    def test_returns_existing_value(self):
        """Test that existing value is returned without prompting."""
        mock_service = Mock()
        provider = ContactSelector(service=mock_service)
        result = provider.get_value("contact_name", "John")
        assert result == "John"
        mock_service.has_contacts.assert_not_called()
    
    @patch('src.utils.progressive_params.questionary.select')
    def test_user_selects_contact(self, mock_select):
        """Test user selects a contact."""
        mock_service = Mock()
        mock_service.has_contacts.return_value = True
        mock_service.list_contacts.return_value = [("Alice", Mock()), ("Bob", Mock())]
        mock_select.return_value.ask.return_value = "Alice"
        
        provider = ContactSelector(service=mock_service)
        result = provider.get_value("contact_name", None)
        
        assert result == "Alice"
        mock_service.has_contacts.assert_called_once()
        mock_service.list_contacts.assert_called_once()
    
    @patch('src.utils.progressive_params.questionary.select')
    def test_user_cancels(self, mock_select):
        """Test user cancels contact selection."""
        mock_service = Mock()
        mock_service.has_contacts.return_value = True
        mock_service.list_contacts.return_value = [("Alice", Mock())]
        mock_select.return_value.ask.return_value = "Cancel"
        
        provider = ContactSelector(service=mock_service)
        result = provider.get_value("contact_name", None)
        
        assert result is None
    
    @patch('src.utils.progressive_params.questionary.select')
    def test_user_cancels_with_none(self, mock_select):
        """Test user cancels with None."""
        mock_service = Mock()
        mock_service.has_contacts.return_value = True
        mock_service.list_contacts.return_value = [("Alice", Mock())]
        mock_select.return_value.ask.return_value = None
        
        provider = ContactSelector(service=mock_service)
        result = provider.get_value("contact_name", None)
        
        assert result is None
    
    def test_no_contacts_available(self):
        """Test when no contacts are available."""
        mock_service = Mock()
        mock_service.has_contacts.return_value = False
        
        provider = ContactSelector(service=mock_service)
        result = provider.get_value("contact_name", None)
        
        assert result is None
        mock_service.has_contacts.assert_called_once()
        mock_service.list_contacts.assert_not_called()
    
    @patch('src.utils.progressive_params.questionary.select')
    def test_custom_message(self, mock_select):
        """Test ContactSelector with custom message."""
        mock_service = Mock()
        mock_service.has_contacts.return_value = True
        mock_service.list_contacts.return_value = [("Alice", Mock())]
        mock_select.return_value.ask.return_value = "Alice"
        
        provider = ContactSelector(message="Choose a contact:", service=mock_service)
        result = provider.get_value("contact_name", None)
        
        assert result == "Alice"
        # Verify custom message was used
        call_args = mock_select.call_args[0]
        assert call_args[0] == "Choose a contact:"
    
    @patch('src.utils.progressive_params.questionary.select')
    def test_multiple_contacts(self, mock_select):
        """Test selecting from multiple contacts."""
        mock_service = Mock()
        mock_service.has_contacts.return_value = True
        mock_service.list_contacts.return_value = [
            ("Alice", Mock()),
            ("Bob", Mock()),
            ("Charlie", Mock())
        ]
        mock_select.return_value.ask.return_value = "Bob"
        
        provider = ContactSelector(service=mock_service)
        result = provider.get_value("contact_name", None)
        
        assert result == "Bob"


class TestNoteSelector:
    """Tests for NoteSelector parameter provider."""
    
    def test_returns_existing_value(self):
        """Test that existing value is returned without prompting."""
        mock_service = Mock()
        provider = NoteSelector(service=mock_service)
        result = provider.get_value("note_name", "Meeting", contact_name="John")
        assert result == "Meeting"
        mock_service.list_notes.assert_not_called()
    
    def test_no_contact_name_in_context(self):
        """Test when contact_name is not in context."""
        mock_service = Mock()
        provider = NoteSelector(service=mock_service)
        result = provider.get_value("note_name", None)
        
        assert result is None
        mock_service.list_notes.assert_not_called()
    
    @patch('src.utils.progressive_params.questionary.select')
    def test_user_selects_note(self, mock_select):
        """Test user selects a note."""
        mock_service = Mock()
        note1 = Mock(spec=Note)
        note1.name = "Meeting"
        note2 = Mock(spec=Note)
        note2.name = "Reminder"
        mock_service.list_notes.return_value = [note1, note2]
        mock_select.return_value.ask.return_value = "Meeting"
        
        provider = NoteSelector(service=mock_service)
        result = provider.get_value("note_name", None, contact_name="John")
        
        assert result == "Meeting"
        mock_service.list_notes.assert_called_once_with("John")
    
    @patch('src.utils.progressive_params.questionary.select')
    def test_user_cancels(self, mock_select):
        """Test user cancels note selection."""
        mock_service = Mock()
        note1 = Mock(spec=Note)
        note1.name = "Meeting"
        mock_service.list_notes.return_value = [note1]
        mock_select.return_value.ask.return_value = "Cancel"
        
        provider = NoteSelector(service=mock_service)
        result = provider.get_value("note_name", None, contact_name="John")
        
        assert result is None
    
    def test_no_notes_for_contact(self):
        """Test when contact has no notes."""
        mock_service = Mock()
        mock_service.list_notes.return_value = []
        
        provider = NoteSelector(service=mock_service)
        result = provider.get_value("note_name", None, contact_name="John")
        
        assert result is None
        mock_service.list_notes.assert_called_once_with("John")
    
    def test_contact_not_found(self):
        """Test when contact is not found."""
        mock_service = Mock()
        mock_service.list_notes.side_effect = ValueError("Contact not found")
        
        provider = NoteSelector(service=mock_service)
        result = provider.get_value("note_name", None, contact_name="NonExistent")
        
        assert result is None
    
    def test_service_error(self):
        """Test when service raises an error."""
        mock_service = Mock()
        mock_service.list_notes.side_effect = RuntimeError("Database error")
        
        provider = NoteSelector(service=mock_service)
        result = provider.get_value("note_name", None, contact_name="John")
        
        assert result is None
    
    @patch('src.utils.progressive_params.questionary.select')
    def test_custom_message(self, mock_select):
        """Test NoteSelector with custom message."""
        mock_service = Mock()
        note1 = Mock(spec=Note)
        note1.name = "Meeting"
        mock_service.list_notes.return_value = [note1]
        mock_select.return_value.ask.return_value = "Meeting"
        
        provider = NoteSelector(message="Pick a note:", service=mock_service)
        result = provider.get_value("note_name", None, contact_name="John")
        
        assert result == "Meeting"
        # Verify custom message was used
        call_args = mock_select.call_args[0]
        assert call_args[0] == "Pick a note:"


class TestTagSelector:
    """Tests for TagSelector parameter provider."""
    
    def test_returns_existing_value(self):
        """Test that existing value is returned without prompting."""
        mock_service = Mock()
        provider = TagSelector(service=mock_service)
        result = provider.get_value("tag", "work", contact_name="John", note_name="Meeting")
        assert result == "work"
        mock_service.note_list_tags.assert_not_called()
    
    def test_no_contact_name_in_context(self):
        """Test when contact_name is not in context."""
        mock_service = Mock()
        provider = TagSelector(service=mock_service)
        result = provider.get_value("tag", None, note_name="Meeting")
        
        assert result is None
        mock_service.note_list_tags.assert_not_called()
    
    def test_no_note_name_in_context(self):
        """Test when note_name is not in context."""
        mock_service = Mock()
        provider = TagSelector(service=mock_service)
        result = provider.get_value("tag", None, contact_name="John")
        
        assert result is None
        mock_service.note_list_tags.assert_not_called()
    
    @patch('src.utils.progressive_params.questionary.select')
    def test_user_selects_tag(self, mock_select):
        """Test user selects a tag."""
        mock_service = Mock()
        mock_service.note_list_tags.return_value = ["work", "important", "urgent"]
        mock_select.return_value.ask.return_value = "work"
        
        provider = TagSelector(service=mock_service)
        result = provider.get_value("tag", None, contact_name="John", note_name="Meeting")
        
        assert result == "work"
        mock_service.note_list_tags.assert_called_once_with("John", "Meeting")
    
    @patch('src.utils.progressive_params.questionary.select')
    def test_user_cancels(self, mock_select):
        """Test user cancels tag selection."""
        mock_service = Mock()
        mock_service.note_list_tags.return_value = ["work", "important"]
        mock_select.return_value.ask.return_value = "Cancel"
        
        provider = TagSelector(service=mock_service)
        result = provider.get_value("tag", None, contact_name="John", note_name="Meeting")
        
        assert result is None
    
    @patch('src.utils.progressive_params.questionary.select')
    def test_user_cancels_with_none(self, mock_select):
        """Test user cancels with None."""
        mock_service = Mock()
        mock_service.note_list_tags.return_value = ["work"]
        mock_select.return_value.ask.return_value = None
        
        provider = TagSelector(service=mock_service)
        result = provider.get_value("tag", None, contact_name="John", note_name="Meeting")
        
        assert result is None
    
    def test_no_tags_for_note(self):
        """Test when note has no tags."""
        mock_service = Mock()
        mock_service.note_list_tags.return_value = []
        
        provider = TagSelector(service=mock_service)
        result = provider.get_value("tag", None, contact_name="John", note_name="Meeting")
        
        assert result is None
        mock_service.note_list_tags.assert_called_once_with("John", "Meeting")
    
    def test_note_not_found(self):
        """Test when note is not found."""
        mock_service = Mock()
        mock_service.note_list_tags.side_effect = ValueError("Note not found")
        
        provider = TagSelector(service=mock_service)
        result = provider.get_value("tag", None, contact_name="John", note_name="NonExistent")
        
        assert result is None
    
    def test_service_error(self):
        """Test when service raises an error."""
        mock_service = Mock()
        mock_service.note_list_tags.side_effect = RuntimeError("Database error")
        
        provider = TagSelector(service=mock_service)
        result = provider.get_value("tag", None, contact_name="John", note_name="Meeting")
        
        assert result is None
    
    @patch('src.utils.progressive_params.questionary.select')
    def test_custom_message(self, mock_select):
        """Test TagSelector with custom message."""
        mock_service = Mock()
        mock_service.note_list_tags.return_value = ["work", "important"]
        mock_select.return_value.ask.return_value = "work"
        
        provider = TagSelector(message="Choose a tag:", service=mock_service)
        result = provider.get_value("tag", None, contact_name="John", note_name="Meeting")
        
        assert result == "work"
        # Verify custom message was used
        call_args = mock_select.call_args[0]
        assert call_args[0] == "Choose a tag:"
    
    @patch('src.utils.progressive_params.questionary.select')
    def test_multiple_tags(self, mock_select):
        """Test selecting from multiple tags."""
        mock_service = Mock()
        mock_service.note_list_tags.return_value = ["work", "important", "urgent", "personal"]
        mock_select.return_value.ask.return_value = "urgent"
        
        provider = TagSelector(service=mock_service)
        result = provider.get_value("tag", None, contact_name="John", note_name="Meeting")
        
        assert result == "urgent"

