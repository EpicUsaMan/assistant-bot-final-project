"""
All command - Show all contacts in the address book.

Commands are Controllers + View in MVCS pattern.
They handle user input, call services, handle exceptions, and display results.
"""

from typing import Optional

import typer
from dependency_injector.wiring import inject, Provide
from rich.console import Console
from rich.panel import Panel
from src.container import Container
from src.services.contact_service import ContactService, ContactSortBy
from src.utils.command_decorators import handle_service_errors

app = typer.Typer()
console = Console()


@inject
@handle_service_errors
def _all_impl(
    sort_by: Optional[ContactSortBy] = None,
    group: Optional[str] = None,
    service: ContactService = Provide[Container.contact_service],
):
    if not service.has_contacts():
        console.print("[yellow]Address book is empty.[/yellow]")
        return

    message = service.get_all_contacts(sort_by=sort_by, group=group)
    console.print(
        Panel(
            message,
            title="[bold]All Contacts[/bold]",
            border_style="cyan",
        )
    )


@app.command(name="all")
def all_command(
    sort_by: Optional[ContactSortBy] = typer.Option(
        None,
        "--sort-by",
        help="Sort by: name, phone, birthday, tag_count or tag_name",
    ),
    group: Optional[str] = typer.Option(
        None,
        "--group",
        help="Group filter: current (default), all or specific group id",
    ),
):
    """
    Show all contacts in the address book.

    This command acts as both Controller and View:
    - Controller: Handles exceptions and coordinates service calls
    - View: Formats and displays results using Rich
    """
    return _all_impl(sort_by=sort_by, group=group)