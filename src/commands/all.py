"""
All command - Show all contacts in the address book.

Commands are Controllers + View in MVCS pattern.
They handle user input, call services, handle exceptions, and display results.
"""

import typer
from dependency_injector.wiring import inject, Provide
from rich.console import Console
from rich.panel import Panel
from src.container import Container
from src.services.contact_service import ContactService
from src.utils.command_decorators import handle_service_errors

app = typer.Typer()
console = Console()


@inject
@handle_service_errors
def _all_impl(
    service: ContactService = Provide[Container.contact_service],
):
    if not service.has_contacts():
        console.print("[yellow]No contacts in the address book.[/yellow]")
    else:
        message = service.get_all_contacts()
        console.print(
            Panel(
                message,
                title="[bold]All Contacts[/bold]",
                border_style="cyan"
            )
        )


@app.command(name="all")
def all_command():
    """
    Show all contacts in the address book.
    
    This command acts as both Controller and View:
    - Controller: Handles exceptions and coordinates service calls
    - View: Formats and displays results using Rich
    """
    return _all_impl()

