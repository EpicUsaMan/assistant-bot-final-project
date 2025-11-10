"""
Delete command - Remove a contact from the address book.

Commands are Controllers + View in MVCS pattern.
They handle user input, call services, handle exceptions, and display results.
"""

import typer
from dependency_injector.wiring import inject, Provide
from rich.console import Console
from src.container import Container
from src.services.contact_service import ContactService
from src.utils.command_decorators import handle_service_errors, auto_save

app = typer.Typer()
console = Console()


@inject
@handle_service_errors
@auto_save
def _delete_impl(
    name: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    message = service.delete_contact(name)
    console.print(f"[bold green]{message}[/bold green]")


@app.command(name="delete")
def delete_command(
    name: str = typer.Argument(..., help="Contact name to delete"),
):
    """
    Delete a contact from the address book.
    
    This command acts as both Controller and View:
    - Controller: Handles exceptions and coordinates service calls
    - View: Formats and displays results using Rich
    """
    return _delete_impl(name)