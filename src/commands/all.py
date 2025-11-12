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
from rich.tree import Tree

app = typer.Typer()
console = Console()

def show_address_book_tree(book: dict) -> Tree:
    tree = Tree("[bold cyan]Address Book[/]")

    # sort by name (key of the dictionary)
    for name in sorted(book.keys(), key=lambda x: x.lower()):
        record = book[name]
        node = tree.add(f"[bold green]{record.name}[/]")

        # phones
        if record.phones:
            phones_node = node.add(f"📞 [bold cyan]Phone:[/] ({len(record.phones)})")
            for phone in record.phones:
                phones_node.add(f"{phone}")
        else:
            node.add("📞 [bold cyan]Phone:[/] [dim]нет[/]")

        # birthday
        if getattr(record, "birthday", None):
            node.add(f"🎂 [bold cyan]Birthday:[/] {record.birthday}")
        else:
            node.add("🎂 [bold cyan]Birthday:[/] [dim]not available[/]")

        # address
        if getattr(record, "address", None):
            node.add(f"🏠 [bold cyan]Address:[/] {record.address}")
        else:
            node.add("🏠 [bold cyan]Address:[/] [dim]not available[/]")

        # email
        if getattr(record, "email", None):
            node.add(f"✉️  [bold cyan]Email:[/] {record.email}")
        else:
            node.add("✉️  [bold cyan]Email:[/] [dim]not available[/]")

    return tree

@inject
@handle_service_errors
def _all_impl(
    sort_by: Optional[ContactSortBy] = None,
    service: ContactService = Provide[Container.contact_service],
):
    if not service.has_contacts():
        console.print("[yellow]No contacts in the address book.[/yellow]")
    else:
        console.print(show_address_book_tree(service.address_book.data))


@app.command(name="all")
def all_command(
    sort_by: Optional[ContactSortBy] = typer.Option(
        None,
        "--sort-by",
        help="Sort by: name, phone, birthday, tag_count or tag_name",
    ),
):
    """
    Show all contacts in the address book.

    This command acts as both Controller and View:
    - Controller: Handles exceptions and coordinates service calls
    - View: Formats and displays results using Rich
    """
    return _all_impl(sort_by=sort_by)