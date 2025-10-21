"""
Dependency Injection container for the application.

This module defines the DI container that manages all application dependencies,
following the Model-View-Controller-Service (MVCS) pattern.
"""

from dependency_injector import containers, providers
from src.models.address_book import AddressBook
from src.services.contact_service import ContactService


class Container(containers.DeclarativeContainer):
    """
    Application DI container following MVCS pattern.
    
    Dependency hierarchy:
    - Model: AddressBook (handles data and serialization)
    - Service: ContactService (business logic)
    - Command: CLI commands (Controller + View - handle coordination and presentation)
    
    Commands ARE controllers in this architecture. They:
    - Receive user input via Typer
    - Call service methods
    - Handle exceptions
    - Format and display results using Rich
    
    This container manages all application dependencies:
    - Address book model instance (handles its own persistence)
    - Contact service for business logic
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
    
    def save_data(self) -> None:
        """
        Save the current address book state to disk.
        
        Models handle their own serialization - we just call the model's method.
        """
        book = self.address_book()
        filename = self.config.storage.filename()
        book.save_to_file(filename)

