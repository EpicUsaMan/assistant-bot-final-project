"""
Change command - Change an existing contact's phone number.

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
def _change_impl(
    name: str,
    old_phone: str,
    new_phone: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    message = service.change_contact(name, old_phone, new_phone)
    console.print(f"[bold green]{message}[/bold green]")


@app.command(name="change")
def change_command(
    name: str = typer.Argument(..., help="Contact name"),
    old_phone: str = typer.Argument(
        ...,
        help="Old phone number",
        callback=validate_phone,
    ),
    new_phone: str = typer.Argument(
        ...,
        help="New phone number",
        callback=validate_phone,
    ),
):
    """
    Change an existing contact's phone number.
    
    This command acts as both Controller and View:
    - Controller: Handles exceptions and coordinates service calls
    - View: Formats and displays results using Rich
    """
    return _change_impl(name, old_phone, new_phone)

