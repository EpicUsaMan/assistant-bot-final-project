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

import questionary
from rich.console import Console
from typing import TYPE_CHECKING
from dependency_injector.wiring import Provide, inject

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


class ContactSelector(ParameterProvider):
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
        self.message = message
        self.service = service
    
    def get_value(self, param_name: str, current_value: Any, **context: Any) -> Optional[str]:
        """Select a contact from available contacts."""
        if current_value is not None:
            return current_value
        
        # Check if contacts exist
        if not self.service.has_contacts():
            console.print("[yellow]No contacts available. Please add contacts first.[/yellow]")
            return None
        
        # Get contact list from service
        contacts = self.service.list_contacts()
        contact_names = [name for name, _ in contacts]
        
        # Show select menu
        selected = questionary.select(
            self.message,
            choices=contact_names + ["Cancel"],
            style=questionary.Style([
                ('selected', 'fg:cyan bold'),
                ('pointer', 'fg:cyan bold'),
            ])
        ).ask()
        
        if selected is None or selected == "Cancel":
            console.print("[yellow]Operation cancelled.[/yellow]")
            return None
        
        return selected


class NoteSelector(ParameterProvider):
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
        self.message = message
        self.service = service
    
    def get_value(self, param_name: str, current_value: Any, **context: Any) -> Optional[str]:
        """Select a note from contact's notes."""
        if current_value is not None:
            return current_value
        
        # Get contact_name from context
        contact_name = context.get('contact_name')
        if not contact_name:
            console.print("[red]Error: Contact must be selected first[/red]")
            return None
        
        # Get notes for contact using service
        try:
            notes = self.service.list_notes(contact_name)
            if not notes:
                console.print(f"[yellow]No notes found for {contact_name}.[/yellow]")
                return None
            
            note_names = [note.name for note in notes]
            
        except ValueError as e:
            console.print(f"[yellow]{e}[/yellow]")
            return None
        except Exception as e:
            console.print(f"[red]Error loading notes: {e}[/red]")
            return None
        
        # Show select menu
        selected = questionary.select(
            self.message,
            choices=note_names + ["Cancel"],
            style=questionary.Style([
                ('selected', 'fg:cyan bold'),
                ('pointer', 'fg:cyan bold'),
            ])
        ).ask()
        
        if selected is None or selected == "Cancel":
            console.print("[yellow]Operation cancelled.[/yellow]")
            return None
        
        return selected


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
        import typer
        
        try:
            result = typer.prompt(
                self.message,
                default=self.default if self.default else None,
                type=str
            )
        except (EOFError, KeyboardInterrupt):
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


class TagSelector(ParameterProvider):
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
        self.message = message
        self.service = service
    
    def get_value(self, param_name: str, current_value: Any, **context: Any) -> Optional[str]:
        """Select a tag from note's tags."""
        if current_value is not None:
            return current_value
        
        # Get contact_name and note_name from context
        contact_name = context.get('contact_name')
        note_name = context.get('note_name')
        
        if not contact_name:
            console.print("[red]Error: Contact must be selected first[/red]")
            return None
        
        if not note_name:
            console.print("[red]Error: Note must be selected first[/red]")
            return None
        
        # Get tags for note using service
        try:
            tags_list = self.service.note_list_tags(contact_name, note_name)
            if not tags_list:
                console.print(f"[yellow]No tags found for note '{note_name}'.[/yellow]")
                return None
            
        except ValueError as e:
            console.print(f"[yellow]{e}[/yellow]")
            return None
        except Exception as e:
            console.print(f"[red]Error loading tags: {e}[/red]")
            return None
        
        # Show select menu
        selected = questionary.select(
            self.message,
            choices=tags_list + ["Cancel"],
            style=questionary.Style([
                ('selected', 'fg:cyan bold'),
                ('pointer', 'fg:cyan bold'),
            ])
        ).ask()
        
        if selected is None or selected == "Cancel":
            console.print("[yellow]Operation cancelled.[/yellow]")
            return None
        
        return selected


class SelectInput(ParameterProvider):
    """
    Provides selection from a list of choices.
    
    Generic selector that can be used for any enum-like selection.
    """
    
    def __init__(
        self,
        message: str,
        choices: list[tuple[str, str]],  # List of (value, display_text) tuples
        required: bool = True
    ):
        self.message = message
        self.choices = choices
        self.required = required
    
    def get_value(self, param_name: str, current_value: Any, **context: Any) -> Optional[str]:
        """Select from a list of choices."""
        if current_value is not None:
            return current_value
        
        # Build display choices
        display_choices = [display for value, display in self.choices]
        display_choices.append("Cancel")
        
        # Show select menu
        selected_display = questionary.select(
            self.message,
            choices=display_choices,
            style=questionary.Style([
                ('selected', 'fg:cyan bold'),
                ('pointer', 'fg:cyan bold'),
            ])
        ).ask()
        
        if selected_display is None or selected_display == "Cancel":
            if self.required:
                console.print("[yellow]Operation cancelled.[/yellow]")
                return None
            else:
                return self.choices[0][0] if self.choices else None
        
        # Find the value for the selected display text
        for value, display in self.choices:
            if display == selected_display:
                return value
        
        return None


class CountrySelector(ParameterProvider):
    """
    Provides country selection from locations catalog.
    
    Shows a select menu with countries from the catalog.
    """
    
    def __init__(self, message: str = "Select country:"):
        """
        Initialize CountrySelector.
        
        Args:
            message: Prompt message for selection
        """
        self.message = message
    
    def get_value(self, param_name: str, current_value: Any, **context: Any) -> Optional[str]:
        """Select a country from catalog."""
        if current_value is not None:
            return current_value
        
        from src.utils.locations import get_catalog
        
        catalog = get_catalog()
        countries = catalog.get_countries()
        
        if not countries:
            console.print("[yellow]No countries available in catalog.[/yellow]")
            return None
        
        # Build choices for SelectInput: (country_code, "Code - Name")
        choices = [(code, f"{code} - {name}") for code, name in countries]
        
        # Use SelectInput for selection
        selector = SelectInput(self.message, choices, required=True)
        return selector.get_value(param_name, current_value, **context)


class CitySelector(ParameterProvider):
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
        self.message = message
    
    def get_value(self, param_name: str, current_value: Any, **context: Any) -> Optional[str]:
        """Select a city from catalog or add new one."""
        if current_value is not None:
            return current_value
        
        # Get country_code from context
        country_code = context.get('country_code') or context.get('country')
        if not country_code:
            console.print("[red]Error: Country must be selected first[/red]")
            return None
        
        from src.utils.locations import get_catalog
        
        catalog = get_catalog()
        
        # Check if country exists
        if not catalog.has_country(country_code):
            console.print(f"[red]Error: Country '{country_code}' not found in catalog[/red]")
            return None
        
        country_name = catalog.get_country_name(country_code) or country_code
        cities = catalog.get_cities(country_code, include_user=True)
        
        # Build choices: (city_name, display_text) + "Add new city" option
        choices = []
        for city in cities:
            marker = " (user)" if catalog.is_user_city(country_code, city) else ""
            choices.append((city, f"{city}{marker}"))
        
        # Add "Add new city" option
        choices.append(("__ADD_NEW__", "[Add new city]"))
        
        # Use SelectInput for selection
        selector = SelectInput(self.message, choices, required=True)
        selected = selector.get_value(param_name, current_value, **context)
        
        if selected == "__ADD_NEW__":
            # User wants to add new city - prompt for city name
            city_input = questionary.text(
                f"Enter city name for {country_name}:",
                validate=lambda text: len(text.strip()) > 0 or "City name cannot be empty"
            ).ask()
            
            if city_input is None:
                console.print("[yellow]Operation cancelled.[/yellow]")
                return None
            
            city_name = city_input.strip()
            
            # Check if city already exists
            if city_name in cities:
                console.print(f"[yellow]City '{city_name}' already exists in catalog[/yellow]")
                return city_name
            
            # City not found - offer to add it (variant A)
            add_confirm = questionary.confirm(
                f"Add '{city_name}' as a new city for {country_name}?",
                default=True
            ).ask()
            
            if add_confirm:
                try:
                    catalog.add_user_city(country_code, city_name)
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
        
        return selected