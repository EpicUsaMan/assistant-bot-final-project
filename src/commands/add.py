"""
Add command - Add a new contact or update existing contact.

Commands are Controllers + View in MVCS pattern.
They handle user input, call services, handle exceptions, and display results.
"""

import typer
from dependency_injector.wiring import inject, Provide
from rich.console import Console
from src.container import Container
from src.services.contact_service import ContactService
from src.utils.validators import validate_phone
from src.utils.command_decorators import handle_service_errors, auto_save

app = typer.Typer()
console = Console()


@inject
@handle_service_errors
@auto_save
def _add_impl(
    name: str,
    phone: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    message = service.add_contact(name, phone)
    console.print(f"[bold green]{message}[/bold green]")


@app.command(name="add")
def add_command(
    name: str = typer.Argument(..., help="Contact name"),
    phone: str = typer.Argument(
        ...,
        help="Phone number (10 digits)",
        callback=validate_phone,
    ),
):
    """
    Add a new contact with a phone number or add a phone to an existing contact.
    
    This command acts as both Controller and View:
    - Controller: Handles exceptions and coordinates service calls
    - View: Formats and displays results using Rich
    """
    return _add_impl(name, phone)

