"""
Add-birthday command - Add a birthday to a contact.

Commands are Controllers + View in MVCS pattern.
They handle user input, call services, handle exceptions, and display results.
"""

import typer
from dependency_injector.wiring import inject, Provide
from rich.console import Console
from src.container import Container
from src.services.contact_service import ContactService
from src.utils.validators import validate_birthday
from src.utils.command_decorators import handle_service_errors, auto_save

app = typer.Typer()
console = Console()


@inject
@handle_service_errors
@auto_save
def _add_birthday_impl(
    name: str,
    birthday: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    message = service.add_birthday(name, birthday)
    console.print(f"[bold green]{message}[/bold green]")


@app.command(name="add-birthday")
def add_birthday_command(
    name: str = typer.Argument(..., help="Contact name"),
    birthday: str = typer.Argument(
        ...,
        help="Birthday in DD.MM.YYYY format",
        callback=validate_birthday,
    ),
):
    """
    Add a birthday date to a contact.
    
    This command acts as both Controller and View:
    - Controller: Handles exceptions and coordinates service calls
    - View: Formats and displays results using Rich
    """
    return _add_birthday_impl(name, birthday)

