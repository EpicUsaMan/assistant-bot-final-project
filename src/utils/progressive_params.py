"""
Progressive parameter fulfillment system for Typer commands.

This module provides a decorator that automatically handles missing parameters
by prompting users interactively. It supports different fulfillment strategies
for different parameter types.

Usage:
    @app.command()
    @progressive_params(
        contact_name=ContactSelector(),
        note_name=TextInput("Note name/title:", required=True),
        content=TextInput("Note content (optional):", required=False)
    )
    def add_note_command(
        contact_name: Optional[str] = None,
        note_name: Optional[str] = None,
        content: Optional[str] = None
    ):
        # All parameters are guaranteed to be filled here
        _add_note_impl(contact_name, note_name, content)
"""

import inspect
import types
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, TypeVar

import click
import questionary
import typer
from rich.console import Console
from typing import TYPE_CHECKING
from dependency_injector.wiring import Provide, inject
from src.utils.locations import get_catalog

if TYPE_CHECKING:
    from src.services.note_service import NoteService
    from src.container import Container

console = Console()
F = TypeVar('F', bound=Callable[..., Any])


class ParameterProvider(ABC):
    """
    Abstract base class for parameter providers.
    
    Each provider knows how to collect a missing parameter value
    from the user interactively.
    """
    
    @abstractmethod
    def get_value(self, param_name: str, current_value: Any, **context: Any) -> Optional[Any]:
        """
        Get the parameter value from user.
        
        Args:
            param_name: Name of the parameter
            current_value: Current value (might be None)
            **context: Additional context (like injected services)
            
        Returns:
            The collected value or None if user cancelled
        """
        pass


class BaseSelector(ParameterProvider):
    """
    Base class for all selector providers with standardized behavior.
    
    Handles common patterns:
    - None/Cancel option handling
    - Operation cancelled messages
    - Questionary select with consistent styling
    - Empty choices validation
    
    Subclasses only need to implement get_choices() method.
    """
    
    def __init__(
        self,
        message: str,
        required: bool = True,
        cancel_message: str = "Operation cancelled.",
        empty_message: Optional[str] = None,
        show_cancel: bool = True
    ):
        """
        Initialize BaseSelector.
        
        Args:
            message: Prompt message for selection
            required: Whether selection is required
            cancel_message: Message to show when user cancels
            empty_message: Message to show when no choices available
            show_cancel: Whether to show Cancel option in menu
        """
        self.message = message
        self.required = required
        self.cancel_message = cancel_message
        self.empty_message = empty_message
        self.show_cancel = show_cancel
        self._select_style = questionary.Style([
            ('selected', 'fg:cyan bold'),
            ('pointer', 'fg:cyan bold'),
        ])
    
    @abstractmethod
    def get_choices(self, current_value: Any, **context: Any) -> Optional[list[str]]:
        """
        Get list of choices for selection.
        
        Args:
            current_value: Current parameter value
            **context: Additional context from other parameters
            
        Returns:
            List of choice strings, or None if choices cannot be retrieved
        """
        pass
    
    def get_value(self, param_name: str, current_value: Any, **context: Any) -> Optional[str]:
        """
        Get selection from user with standardized behavior.
        
        Args:
            param_name: Name of the parameter
            current_value: Current value (might be None)
            **context: Additional context from other parameters
            
        Returns:
            Selected value or None if cancelled
        """
        if current_value is not None:
            return current_value
        
        # Get choices from subclass
        choices = self.get_choices(current_value, **context)
        
        # Handle no choices available
        if choices is None:
            return None
        
        if not choices:
            if self.empty_message:
                console.print(f"[yellow]{self.empty_message}[/yellow]")
            return None
        
        # Add Cancel option if needed
        display_choices = choices + (["Cancel"] if self.show_cancel else [])
        
        # Show select menu
        selected = questionary.select(
            self.message,
            choices=display_choices,
            style=self._select_style
        ).ask()
        
        # Handle cancellation
        if selected is None or (self.show_cancel and selected == "Cancel"):
            if self.required and self.cancel_message:
                console.print(f"[yellow]{self.cancel_message}[/yellow]")
            return None
        
        return selected


class ContactSelector(BaseSelector):
    """
    Provides contact selection from available contacts.
    
    Shows a select menu with arrow keys navigation.
    Uses dependency injection for service access.
    """
    
    @inject
    def __init__(
        self,
        message: str = "Select contact:",
        service: "NoteService" = Provide["Container.note_service"]
    ):
        """
        Initialize ContactSelector.
        
        Args:
            message: Prompt message for selection
            service: NoteService instance (injected by container as singleton)
        """
        super().__init__(
            message=message,
            empty_message="No contacts available. Please add contacts first."
        )
        self.service = service
    
    def get_choices(self, current_value: Any, **context: Any) -> Optional[list[str]]:
        """Get list of available contacts."""
        if not self.service.has_contacts():
            return []
        
        contacts = self.service.list_contacts()
        return [name for name, _ in contacts]


class NoteSelector(BaseSelector):
    """
    Provides note selection from a contact's notes.
    
    Requires contact_name parameter to be filled first.
    Uses dependency injection for service access.
    """
    
    @inject
    def __init__(
        self,
        message: str = "Select note:",
        service: "NoteService" = Provide["Container.note_service"]
    ):
        """
        Initialize NoteSelector.
        
        Args:
            message: Prompt message for selection
            service: NoteService instance (injected by container as singleton)
        """
        super().__init__(message=message)
        self.service = service
    
    def get_choices(self, current_value: Any, **context: Any) -> Optional[list[str]]:
        """Get list of notes for the contact."""
        contact_name = context.get('contact_name')
        if not contact_name:
            console.print("[red]Error: Contact must be selected first[/red]")
            return None
        
        try:
            notes = self.service.list_notes(contact_name)
            if not notes:
                console.print(f"[yellow]No notes found for {contact_name}.[/yellow]")
                return None
            
            return [note.name for note in notes]
            
        except ValueError as e:
            console.print(f"[yellow]{e}[/yellow]")
            return None
        except Exception as e:
            console.print(f"[red]Error loading notes: {e}[/red]")
            return None


class GroupSelector(BaseSelector):
    """
    Provides group selection from available groups.
    
    Shows a select menu with arrow keys navigation.
    Uses dependency injection for service access.
    """
    
    @inject
    def __init__(
        self,
        message: str = "Select group:",
        service = Provide["Container.contact_service"]
    ):
        """
        Initialize GroupSelector.
        
        Args:
            message: Prompt message for selection
            service: ContactService instance (injected by container as singleton)
        """
        super().__init__(
            message=message,
            empty_message="No groups available. Please add groups first."
        )
        self.service = service
    
    def get_choices(self, current_value: Any, **context: Any) -> Optional[list[str]]:
        """Get list of available groups."""
        groups = self.service.list_groups()
        if not groups:
            return []
        
        return [group_id for group_id, _ in groups]


class TextInput(ParameterProvider):
    """
    Provides text input for a parameter.
    
    Supports both required and optional text inputs.
    Can be configured with validation and multiline support.
    """
    
    def __init__(
        self,
        message: str,
        required: bool = True,
        multiline: bool = False,
        default: str = "",
        validator: Optional[Callable[[str], bool]] = None,
        error_message: str = "Invalid input"
    ):
        self.message = message
        self.required = required
        self.multiline = multiline
        self.default = default
        self.validator = validator
        self.error_message = error_message
    
    def get_value(self, param_name: str, current_value: Any, **context: Any) -> Optional[str]:
        """Get text input from user."""
        if current_value is not None:
            return current_value
        
        # Build validation function
        validation = None
        if self.required:
            validation = lambda text: (
                len(text.strip()) > 0 or f"{param_name.replace('_', ' ').title()} cannot be empty"
            )
        elif self.validator:
            validation = lambda text: (
                self.validator(text) or self.error_message
            )
        
        # Get input
        result = questionary.text(
            self.message,
            multiline=self.multiline,
            default=self.default,
            validate=validation
        ).ask()
        
        if result is None:
            if self.required:
                console.print("[yellow]Operation cancelled.[/yellow]")
                return None
            else:
                return self.default
        
        return result


class EmailInput(ParameterProvider):
    """
    Specialized input provider for email addresses using typer.prompt.
    
    WHY typer.prompt instead of questionary.text?
    ==============================================
    
    The questionary library uses prompt_toolkit under the hood, which has
    compatibility issues with PowerShell on Windows when handling the '@' symbol.
    Even when users try to escape it or use quotes, the '@' character often
    fails to be captured correctly in interactive prompts.
    
    typer.prompt uses Python's standard input() function, which:
    - Works reliably across all platforms (Windows PowerShell, CMD, Linux, Mac)
    - Properly handles special characters like '@' without issues
    - Provides consistent behavior regardless of terminal/shell
    - Is simpler and more predictable for single-line text input
    
    This ensures users can always enter email addresses correctly, even in
    PowerShell environments where questionary has known limitations.
    
    Trade-offs:
    - Less fancy UI (no rich formatting during input)
    - Still provides clean, functional email input
    - Better reliability > fancy UI for critical input like email
    """
    
    def __init__(
        self,
        message: str,
        required: bool = True,
        default: str = "",
    ):
        """
        Initialize email input provider.
        
        Args:
            message: Prompt message to display
            required: Whether email is required (default: True)
            default: Default value if user just presses Enter (default: empty)
        """
        self.message = message
        self.required = required
        self.default = default
    
    def get_value(self, param_name: str, current_value: Any, **context: Any) -> Optional[str]:
        """
        Get email input from user using typer.prompt.
        
        This method uses typer.prompt instead of questionary to avoid
        PowerShell compatibility issues with the '@' symbol.
        """
        if current_value is not None:
            return current_value
        
        # Use typer.prompt for reliable '@' symbol handling
        # This works correctly in PowerShell, CMD, and all other terminals
        try:
            result = typer.prompt(
                self.message,
                default=self.default if self.default else None,
                type=str
            )
        except (EOFError, KeyboardInterrupt, click.exceptions.Abort):
            # User cancelled (Ctrl+C or Ctrl+Z)
            console.print("[yellow]Operation cancelled.[/yellow]")
            return None
        
        # Handle empty input
        if not result or not result.strip():
            if self.required:
                console.print("[yellow]Email is required.[/yellow]")
                return None
            return self.default if self.default else None
        
        return result.strip()


class ConfirmInput(ParameterProvider):
    """
    Provides yes/no confirmation input.
    """
    
    def __init__(self, message: str, default: bool = False):
        self.message = message
        self.default = default
    
    def get_value(self, param_name: str, current_value: Any, **context: Any) -> Optional[bool]:
        """Get confirmation from user."""
        if current_value is not None:
            return current_value
        
        result = questionary.confirm(
            self.message,
            default=self.default
        ).ask()
        
        return result


class TagsInput(ParameterProvider):
    """
    Provides tags input for parameters that accept multiple tags.
    
    Handles both single tags and comma-separated lists.
    Returns None if user cancels, empty list if input is empty and not required.
    """
    
    def __init__(self, message: str = "Enter tags (comma-separated):", required: bool = True):
        self.message = message
        self.required = required
    
    def get_value(self, param_name: str, current_value: Any, **context: Any) -> Optional[list[str]]:
        """Get tags input from user."""
        # If value is already a list, return it
        if current_value is not None and isinstance(current_value, list):
            return current_value
        
        # If value is a string list from argument, convert to actual list
        if current_value is not None:
            # Already provided as arguments
            return current_value if isinstance(current_value, list) else [current_value]
        
        # Prompt for input
        validation = None
        if self.required:
            validation = lambda text: len(text.strip()) > 0 or "Tags cannot be empty"
        
        result = questionary.text(
            self.message,
            validate=validation
        ).ask()
        
        if result is None:
            if self.required:
                console.print("[yellow]Operation cancelled.[/yellow]")
                return None
            else:
                return []
        
        # Parse comma-separated tags
        if not result.strip():
            return []
        
        # Split by comma and strip whitespace
        tags = [tag.strip() for tag in result.split(',') if tag.strip()]
        return tags if tags else []


class _ProgressiveParamsWrapper:
    """
    Callable wrapper that appears as the original function to Typer.
    
    This class-based wrapper allows us to intercept calls while preserving
    ALL function metadata that Typer needs for inspection, including
    autocompletion callbacks.
    """
    def __init__(self, func: Callable, providers: dict[str, ParameterProvider]):
        self._func = func
        self._providers = providers
        
        # Copy ALL function attributes to make this class instance
        # appear identical to the original function
        self.__name__ = func.__name__
        self.__qualname__ = func.__qualname__
        self.__module__ = func.__module__
        self.__doc__ = func.__doc__
        self.__dict__.update(func.__dict__)
        self.__annotations__ = func.__annotations__
        self.__wrapped__ = func  # For introspection tools
        
        # CRITICAL: Copy function code and defaults
        # Typer inspects these to extract autocompletion callbacks
        if hasattr(func, '__code__'):
            self.__code__ = func.__code__  # type: ignore
        if hasattr(func, '__defaults__'):
            self.__defaults__ = func.__defaults__  # type: ignore
        if hasattr(func, '__kwdefaults__'):
            self.__kwdefaults__ = func.__kwdefaults__  # type: ignore
    
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the function with progressive parameter fulfillment."""
        # Get function signature from original function
        sig = inspect.signature(self._func)
        bound = sig.bind_partial(*args, **kwargs)
        bound.apply_defaults()
        
        # Build context for providers - include all parameters, not just those with providers
        # This allows providers to access other parameters in the context
        context = dict(bound.arguments)
        
        # Process parameters in order
        param_names = list(sig.parameters.keys())
        for param_name in param_names:
            # Skip if not in our providers
            if param_name not in self._providers:
                continue
            
            # Get current value
            current_value = bound.arguments.get(param_name)
            
            # Get provider - call it if it's a factory callable
            provider_or_factory = self._providers[param_name]
            if callable(provider_or_factory) and not isinstance(provider_or_factory, ParameterProvider):
                # Check if it's a functools.partial wrapping a DI provider
                from functools import partial as functools_partial
                from dependency_injector import providers as di_providers
                
                underlying_factory = None
                partial_args = ()
                partial_kwargs = {}
                
                if isinstance(provider_or_factory, functools_partial):
                    # Unwrap the partial to get the underlying factory
                    underlying_factory = provider_or_factory.func
                    partial_args = provider_or_factory.args
                    partial_kwargs = provider_or_factory.keywords
                    provider_or_factory_to_check = underlying_factory
                else:
                    provider_or_factory_to_check = provider_or_factory
                
                # Check if it's a dependency-injector Provider
                # These need to be called on the container instance, not the class
                if isinstance(provider_or_factory_to_check, di_providers.Provider):
                    # It's a DI provider - need to resolve it through the container instance
                    # Find which attribute of Container this provider is
                    from src.main import container
                    from src.container import Container as ContainerClass
                    
                    provider_name = None
                    for attr_name in dir(ContainerClass):
                        if not attr_name.startswith('_'):
                            try:
                                attr_value = getattr(ContainerClass, attr_name)
                                if attr_value is provider_or_factory_to_check:
                                    provider_name = attr_name
                                    break
                            except Exception as e:
                                continue
                    
                    if provider_name:
                        # Call through container instance to use correct DI context
                        # Apply partial args/kwargs if present
                        if underlying_factory:
                            provider = getattr(container, provider_name)(*partial_args, **partial_kwargs)
                        else:
                            provider = getattr(container, provider_name)()
                    else:
                        # Fallback: call directly (might not have correct context)
                        provider = provider_or_factory()
                else:
                    # It's a regular factory callable, call it to get the provider instance
                    provider = provider_or_factory()
            else:
                # It's already a provider instance
                provider = provider_or_factory
            
            # Use provider to get value if missing
            new_value = provider.get_value(param_name, current_value, **context)
            
            # If user cancelled (None returned for required param), stop
            if new_value is None and provider.__class__ not in [TextInput]:
                return None
            elif new_value is None and isinstance(provider, TextInput) and provider.required:
                return None
            
            # Update bound arguments and context
            bound.arguments[param_name] = new_value
            context[param_name] = new_value
        
        # Call original function with filled parameters
        return self._func(**bound.arguments)
    
    def __get__(self, obj: Any, objtype: Any = None) -> Any:
        """Support instance methods."""
        if obj is None:
            return self
        return types.MethodType(self, obj)
    
    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to wrapped function."""
        return getattr(self._func, name)


def progressive_params(
    **param_providers: ParameterProvider | Callable[..., ParameterProvider]
) -> Callable[[F], F]:
    """
    Decorator that automatically fills missing parameters using interactive prompts.
    
    Uses a callable class wrapper that appears identical to the original function,
    allowing Typer to properly inspect autocompletion callbacks.
    
    Args:
        **param_providers: Mapping of parameter names to ParameterProvider instances
                          or callables (factory functions) that return providers
        
    Returns:
        Decorator function
        
    Example:
        @app.command()
        @progressive_params(
            contact_name=Container.contact_selector_factory,
            note_name=partial(Container.text_input_factory, "Note name:", required=True),
            content=partial(Container.text_input_factory, "Content:", required=False)
        )
        def add_note(contact_name: str, note_name: str, content: str):
            # All parameters guaranteed to be filled
            pass
    """
    def decorator(func: F) -> F:
        # Store providers as function attribute for introspection
        func._progressive_param_providers = param_providers  # type: ignore
        
        # Create callable wrapper that preserves all function metadata
        wrapper = _ProgressiveParamsWrapper(func, param_providers)
        
        return wrapper  # type: ignore
    return decorator


class TagSelector(BaseSelector):
    """
    Provides tag selection from a note's tags.
    
    Requires contact_name and note_name parameters to be filled first.
    Uses dependency injection for service access.
    """
    
    @inject
    def __init__(
        self,
        message: str = "Select tag:",
        service: "NoteService" = Provide["Container.note_service"]
    ):
        """
        Initialize TagSelector.
        
        Args:
            message: Prompt message for selection
            service: NoteService instance (injected by container as singleton)
        """
        super().__init__(message=message)
        self.service = service
    
    def get_choices(self, current_value: Any, **context: Any) -> Optional[list[str]]:
        """Get list of tags for the note."""
        contact_name = context.get('contact_name')
        note_name = context.get('note_name')
        
        if not contact_name:
            console.print("[red]Error: Contact must be selected first[/red]")
            return None
        
        if not note_name:
            console.print("[red]Error: Note must be selected first[/red]")
            return None
        
        try:
            tags_list = self.service.note_list_tags(contact_name, note_name)
            if not tags_list:
                console.print(f"[yellow]No tags found for note '{note_name}'.[/yellow]")
                return None
            
            return tags_list
            
        except ValueError as e:
            console.print(f"[yellow]{e}[/yellow]")
            return None
        except Exception as e:
            console.print(f"[red]Error loading tags: {e}[/red]")
            return None


class SelectInput(BaseSelector):
    """
    Provides selection from a list of choices.
    
    Generic selector that can be used for any enum-like selection.
    Supports (value, display_text) tuples for mapping display to actual values.
    """
    
    def __init__(
        self,
        message: str,
        choices: list[tuple[str, str]],  # List of (value, display_text) tuples
        required: bool = True
    ):
        """
        Initialize SelectInput.
        
        Args:
            message: Prompt message for selection
            choices: List of (value, display_text) tuples
            required: Whether selection is required
        """
        super().__init__(message=message, required=required)
        self.choices = choices
        self._value_map = {display: value for value, display in choices}
    
    def get_choices(self, current_value: Any, **context: Any) -> Optional[list[str]]:
        """Get display choices."""
        return [display for value, display in self.choices]
    
    def get_value(self, param_name: str, current_value: Any, **context: Any) -> Optional[str]:
        """
        Select from choices with display-to-value mapping.
        
        Overrides base implementation to handle value mapping.
        """
        if current_value is not None:
            return current_value
        
        # Get choices
        display_choices = self.get_choices(current_value, **context)
        if not display_choices:
            if not self.required:
                return self.choices[0][0] if self.choices else None
            return None
        
        # Add Cancel option if needed
        display_choices_with_cancel = display_choices + (["Cancel"] if self.show_cancel else [])
        
        # Show select menu
        selected_display = questionary.select(
            self.message,
            choices=display_choices_with_cancel,
            style=self._select_style
        ).ask()
        
        # Handle cancellation
        if selected_display is None or (self.show_cancel and selected_display == "Cancel"):
            if self.required:
                if self.cancel_message:
                    console.print(f"[yellow]{self.cancel_message}[/yellow]")
                return None
            else:
                # For optional selections, return first choice as default
                return self.choices[0][0] if self.choices else None
        
        # Map display text back to actual value
        return self._value_map.get(selected_display)


class CountrySelector(BaseSelector):
    """
    Provides country selection from locations catalog with ability to add new countries.
    
    Shows a select menu with countries from the catalog.
    If country is not found in catalog, offers to add it.
    """
    
    def __init__(self, message: str = "Select country:"):
        """
        Initialize CountrySelector.
        
        Args:
            message: Prompt message for selection
        """
        super().__init__(message=message, required=True)
    
    def get_choices(self, current_value: Any, **context: Any) -> Optional[list[str]]:
        """
        Get list of countries with special handling for adding new countries.
        
        Returns display strings for countries, including special "[Add new country]" option.
        """
        catalog = get_catalog()
        countries = catalog.get_countries(include_user=True)
        
        # Store catalog for later use in get_value
        self._catalog = catalog
        self._countries = countries
        
        # Build display choices with markers
        display_choices = []
        for code, name in countries:
            marker = " (user)" if catalog.is_user_country(code) else ""
            display_choices.append(f"{code} - {name}{marker}")
        
        # Add "Add new country" option
        display_choices.append("[Add new country]")
        
        return display_choices
    
    def get_value(self, param_name: str, current_value: Any, **context: Any) -> Optional[str]:
        """
        Select country or add new one.
        
        Overrides base implementation to handle "Add new country" flow.
        """
        if current_value is not None:
            return current_value
        
        # Use base selector to get choice
        display_choices = self.get_choices(current_value, **context)
        if display_choices is None:
            return None
        
        # Show select menu (without Cancel since we handle it ourselves)
        selected_display = questionary.select(
            self.message,
            choices=display_choices + ["Cancel"],
            style=self._select_style
        ).ask()
        
        # Handle cancellation
        if selected_display is None or selected_display == "Cancel":
            if self.cancel_message:
                console.print(f"[yellow]{self.cancel_message}[/yellow]")
            return None
        
        # Handle "Add new country" option
        if selected_display == "[Add new country]":
            return self._handle_add_new_country(param_name, context)
        
        # Extract actual country code (remove " - Name" and marker like " (user)")
        country_code = selected_display.split(" - ")[0]
        return country_code
    
    def _handle_add_new_country(self, param_name: str, context: dict) -> Optional[str]:
        """Handle the flow for adding a new country."""
        # Prompt for country code
        code_input = questionary.text(
            "Enter country code (2-3 letters, e.g., 'UA', 'PL', 'US'):",
            validate=lambda text: (
                len(text.strip()) >= 2 and len(text.strip()) <= 3 and text.strip().isalpha()
            ) or "Country code must be 2-3 letters"
        ).ask()
        
        if code_input is None:
            console.print("[yellow]Operation cancelled.[/yellow]")
            return None
        
        country_code = code_input.strip().upper()
        
        # Check if country already exists
        if self._catalog.has_country(country_code):
            existing_name = self._catalog.get_country_name(country_code)
            console.print(f"[yellow]Country '{country_code}' already exists as '{existing_name}'[/yellow]")
            return country_code
        
        # Prompt for country name
        name_input = questionary.text(
            f"Enter country name for '{country_code}':",
            validate=lambda text: len(text.strip()) > 0 or "Country name cannot be empty"
        ).ask()
        
        if name_input is None:
            console.print("[yellow]Operation cancelled.[/yellow]")
            return None
        
        country_name = name_input.strip()
        
        # Offer to add new country
        add_confirm = questionary.confirm(
            f"Add '{country_code}' ({country_name}) as a new country?",
            default=True
        ).ask()
        
        if add_confirm:
            try:
                self._catalog.add_user_country(country_code, country_name)
                console.print(f"[bold green]Country '{country_code}' ({country_name}) added to catalog[/bold green]")
                return country_code
            except ValueError as e:
                console.print(f"[bold red]Error:[/bold red] {e}")
                # Ask to try again
                if questionary.confirm("Try entering a different country?", default=True).ask():
                    return self.get_value(param_name, None, **context)
                return None
        else:
            # User doesn't want to add - ask to try again
            if questionary.confirm("Select a different country?", default=True).ask():
                return self.get_value(param_name, None, **context)
            return None


class CitySelector(BaseSelector):
    """
    Provides city selection from locations catalog with ability to add new cities.
    
    Requires country_code parameter to be filled first.
    If city is not found in catalog, offers to add it (variant A).
    """
    
    def __init__(self, message: str = "Select city:"):
        """
        Initialize CitySelector.
        
        Args:
            message: Prompt message for selection
        """
        super().__init__(message=message, required=True)
    
    def get_choices(self, current_value: Any, **context: Any) -> Optional[list[str]]:
        """
        Get list of cities with special handling for context validation.
        
        Returns display strings for cities, including special "[Add new city]" option.
        """
        # Get country_code from context
        country_code = context.get('country_code') or context.get('country')
        if not country_code:
            console.print("[red]Error: Country must be selected first[/red]")
            return None
        
        catalog = get_catalog()
        
        # Check if country exists
        if not catalog.has_country(country_code):
            console.print(f"[red]Error: Country '{country_code}' not found in catalog[/red]")
            return None
        
        cities = catalog.get_cities(country_code, include_user=True)
        
        # Store catalog and country info for later use in get_value
        self._catalog = catalog
        self._country_code = country_code
        self._cities = cities
        
        # Build display choices with markers
        display_choices = []
        for city in cities:
            marker = " (user)" if catalog.is_user_city(country_code, city) else ""
            display_choices.append(f"{city}{marker}")
        
        # Add "Add new city" option
        display_choices.append("[Add new city]")
        
        return display_choices
    
    def get_value(self, param_name: str, current_value: Any, **context: Any) -> Optional[str]:
        """
        Select city or add new one.
        
        Overrides base implementation to handle "Add new city" flow.
        """
        if current_value is not None:
            return current_value
        
        # Use base selector to get choice
        display_choices = self.get_choices(current_value, **context)
        if display_choices is None:
            return None
        
        # Show select menu (without Cancel since we handle it ourselves)
        selected_display = questionary.select(
            self.message,
            choices=display_choices + ["Cancel"],
            style=self._select_style
        ).ask()
        
        # Handle cancellation
        if selected_display is None or selected_display == "Cancel":
            if self.cancel_message:
                console.print(f"[yellow]{self.cancel_message}[/yellow]")
            return None
        
        # Handle "Add new city" option
        if selected_display == "[Add new city]":
            return self._handle_add_new_city(param_name, context)
        
        # Extract actual city name (remove marker like " (user)")
        city_name = selected_display.split(" (user)")[0]
        return city_name
    
    def _handle_add_new_city(self, param_name: str, context: dict) -> Optional[str]:
        """Handle the flow for adding a new city."""
        country_name = self._catalog.get_country_name(self._country_code) or self._country_code
        
        # Prompt for city name
        city_input = questionary.text(
            f"Enter city name for {country_name}:",
            validate=lambda text: len(text.strip()) > 0 or "City name cannot be empty"
        ).ask()
        
        if city_input is None:
            console.print("[yellow]Operation cancelled.[/yellow]")
            return None
        
        city_name = city_input.strip()
        
        # Check if city already exists
        if city_name in self._cities:
            console.print(f"[yellow]City '{city_name}' already exists in catalog[/yellow]")
            return city_name
        
        # Offer to add new city
        add_confirm = questionary.confirm(
            f"Add '{city_name}' as a new city for {country_name}?",
            default=True
        ).ask()
        
        if add_confirm:
            try:
                self._catalog.add_user_city(self._country_code, city_name)
                console.print(f"[bold green]City '{city_name}' added to catalog[/bold green]")
                return city_name
            except ValueError as e:
                console.print(f"[bold red]Error:[/bold red] {e}")
                # Ask to try again
                if questionary.confirm("Try entering a different city name?", default=True).ask():
                    return self.get_value(param_name, None, **context)
                return None
        else:
            # User doesn't want to add - ask to try again
            if questionary.confirm("Enter a different city name?", default=True).ask():
                return self.get_value(param_name, None, **context)
            return None