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
from src.utils.progressive_params import ContactSelector, NoteSelector, GroupSelector, TagSelector, TextInput, EmailInput, ConfirmInput, TagsInput, SelectInput, CountrySelector, CitySelector


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
    
    # Contact service (factory - business logic layer)
    contact_service = providers.Factory(
        ContactService,
        address_book=address_book
    )
    
    # Note service (factory - note management business logic)
    note_service = providers.Factory(
        NoteService,
        address_book=address_book
    )
    
    # Search service (factory - search business logic)
    search_service = providers.Factory(
        SearchService,
        address_book=address_book
    )
    
    # Progressive parameter providers (utility layer)
    contact_selector_factory = providers.Factory(
        ContactSelector,
        service=note_service
    )
    
    note_selector_factory = providers.Factory(
        NoteSelector,
        service=note_service
    )
    
    group_selector_factory = providers.Factory(
        GroupSelector,
        service=contact_service
    )
    
    tag_selector_factory = providers.Factory(
        TagSelector,
        service=note_service
    )
    
    text_input_factory = providers.Factory(
        TextInput
    )
    
    email_input_factory = providers.Factory(
        EmailInput
    )
    
    confirm_input_factory = providers.Factory(
        ConfirmInput
    )
    
    tags_input_factory = providers.Factory(
        TagsInput
    )
    
    select_input_factory = providers.Factory(
        SelectInput
    )
    
    country_selector_factory = providers.Factory(
        CountrySelector
    )
    
    city_selector_factory = providers.Factory(
        CitySelector
    )
    
    def save_data(self) -> None:
        """
        Save the current address book state to disk.
        
        Models handle their own serialization - we just call the model's method.
        """
        book = self.address_book()
        filename = self.config.storage.filename()
        book.save_to_file(filename)

