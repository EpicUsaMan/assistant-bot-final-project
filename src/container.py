"""
Dependency Injection container for the application.

This module defines the DI container that manages all application dependencies,
following the Model-View-Controller-Service (MVCS) pattern.
"""

from dependency_injector import containers, providers
from src.models.address_book import AddressBook
from src.services.contact_service import ContactService
from src.services.note_service import NoteService
from src.services.search_service import SearchService

def _get_contact_selector_class():
    """Lazy import ContactSelector class."""
    from src.utils.progressive_params import ContactSelector
    return ContactSelector


def _get_note_selector_class():
    """Lazy import NoteSelector class."""
    from src.utils.progressive_params import NoteSelector
    return NoteSelector


def _get_group_selector_class():
    """Lazy import GroupSelector class."""
    from src.utils.progressive_params import GroupSelector
    return GroupSelector


def _get_tag_selector_class():
    """Lazy import TagSelector class."""
    from src.utils.progressive_params import TagSelector
    return TagSelector


def _get_text_input_class():
    """Lazy import TextInput class."""
    from src.utils.progressive_params import TextInput
    return TextInput


def _get_email_input_class():
    """Lazy import EmailInput class."""
    from src.utils.progressive_params import EmailInput
    return EmailInput


def _get_confirm_input_class():
    """Lazy import ConfirmInput class."""
    from src.utils.progressive_params import ConfirmInput
    return ConfirmInput


def _get_tags_input_class():
    """Lazy import TagsInput class."""
    from src.utils.progressive_params import TagsInput
    return TagsInput


def _get_select_input_class():
    """Lazy import SelectInput class."""
    from src.utils.progressive_params import SelectInput
    return SelectInput


def _get_country_selector_class():
    """Lazy import CountrySelector class."""
    from src.utils.progressive_params import CountrySelector
    return CountrySelector


def _get_city_selector_class():
    """Lazy import CitySelector class."""
    from src.utils.progressive_params import CitySelector
    return CitySelector


class Container(containers.DeclarativeContainer):
    """
    Application DI container following MVCS pattern.
    
    Dependency hierarchy:
    - Model: AddressBook (handles data and serialization)
    - Services: ContactService, NoteService, SearchService (business logic)
    - Command: CLI commands (Controller + View - handle coordination and presentation)
    
    Commands ARE controllers in this architecture. They:
    - Receive user input via Typer
    - Call service methods
    - Handle exceptions
    - Format and display results using Rich
    
    This container manages all application dependencies:
    - Address book model instance (handles its own persistence)
    - Contact service for contact-related business logic
    - Note service for note-related business logic
    - Search service for search-related business logic
    """
    
    config = providers.Configuration()
    
    # Address book model (singleton - loaded once and reused)
    # Models handle their own persistence
    address_book = providers.Singleton(
        lambda filename: AddressBook.load_from_file(filename),
        filename=config.storage.filename.as_(str)
    )
    
    # Contact service (singleton - business logic layer)
    # Services must be singletons because they store references to data
    contact_service = providers.Singleton(
        ContactService,
        address_book=address_book
    )
    
    # Note service (singleton - note management business logic)
    # Services must be singletons because they store references to data
    note_service = providers.Singleton(
        NoteService,
        address_book=address_book
    )
    
    # Search service (singleton - search business logic)
    # Services must be singletons because they store references to data
    search_service = providers.Singleton(
        SearchService,
        address_book=address_book
    )
    
    # Progressive parameter providers (utility layer)
    # Using Callable to lazily get the class, then creating instances
    # Lambda functions accept both *args and **kwargs for flexibility
    contact_selector_factory = providers.Callable(
        lambda *args, **kwargs: _get_contact_selector_class()(*args, **kwargs),
        service=note_service
    )
    
    note_selector_factory = providers.Callable(
        lambda *args, **kwargs: _get_note_selector_class()(*args, **kwargs),
        service=note_service
    )
    
    group_selector_factory = providers.Callable(
        lambda *args, **kwargs: _get_group_selector_class()(*args, **kwargs),
        service=contact_service
    )
    
    tag_selector_factory = providers.Callable(
        lambda *args, **kwargs: _get_tag_selector_class()(*args, **kwargs),
        service=note_service
    )
    
    text_input_factory = providers.Callable(
        lambda *args, **kwargs: _get_text_input_class()(*args, **kwargs)
    )
    
    email_input_factory = providers.Callable(
        lambda *args, **kwargs: _get_email_input_class()(*args, **kwargs)
    )
    
    confirm_input_factory = providers.Callable(
        lambda *args, **kwargs: _get_confirm_input_class()(*args, **kwargs)
    )
    
    tags_input_factory = providers.Callable(
        lambda *args, **kwargs: _get_tags_input_class()(*args, **kwargs)
    )
    
    select_input_factory = providers.Callable(
        lambda *args, **kwargs: _get_select_input_class()(*args, **kwargs)
    )
    
    country_selector_factory = providers.Callable(
        lambda *args, **kwargs: _get_country_selector_class()(*args, **kwargs)
    )
    
    city_selector_factory = providers.Callable(
        lambda *args, **kwargs: _get_city_selector_class()(*args, **kwargs)
    )
    
    def save_data(self) -> None:
        """
        Save the current address book state to disk.
        
        Models handle their own serialization - we just call the model's method.
        """
        book = self.address_book()
        filename = self.config.storage.filename()
        book.save_to_file(filename)

container_instance = Container()