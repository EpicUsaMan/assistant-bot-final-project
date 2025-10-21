"""
Phone command - Show phone numbers for a contact.

Commands are Controllers + View in MVCS pattern.
They handle user input, call services, handle exceptions, and display results.
"""

import typer
from dependency_injector.wiring import inject, Provide
from rich.console import Console
from src.container import Container
from src.services.contact_service import ContactService
from src.utils.command_decorators import handle_service_errors

app = typer.Typer()
console = Console()


@inject
@handle_service_errors
def _phone_impl(
    name: str,
    service: ContactService = Provide[Container.contact_service],
):
    message = service.get_phone(name)
    console.print(f"[bold cyan]{message}[/bold cyan]")


@app.command(name="phone")
def phone_command(
    name: str = typer.Argument(..., help="Contact name"),
):
    """
    Show all phone numbers for a contact.
    
    This command acts as both Controller and View:
    - Controller: Handles exceptions and coordinates service calls
    - View: Formats and displays results using Rich
    """
    return _phone_impl(name)

