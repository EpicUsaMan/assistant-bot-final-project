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

def show_address_book(book: dict) -> Tree:
    tree = Tree("[bold cyan]Address Book[/]")
    root = next(iter(book.values()))
    is_grouped = isinstance(root, dict)

    def add_contact_node(parent: Tree, record) -> None:
        node = parent.add(f"[bold green]{record.name}[/]")

        # phones
        if getattr(record, "phones", None):
            phones_node = node.add(
                f"📞 [cyan]Phone:[/] ({len(record.phones)})"
            )
            for phone in record.phones:
                phones_node.add(f"{phone}")
        else:
            node.add("📞 [cyan]Phone:[/] [dim]not available[/]")

        # birthday
        if getattr(record, "birthday", None):
            node.add(f"🎂 [cyan]Birthday:[/] {record.birthday}")
        else:
            node.add("🎂 [cyan]Birthday:[/] [dim]not available[/]")

        # address
        if getattr(record, "address", None):
            node.add(f"🏠 [cyan]Address:[/] {record.address}")
        else:
            node.add("🏠 [cyan]Address:[/] [dim]not available[/]")

        # email
        if getattr(record, "email", None):
            node.add(f"✉️  [cyan]Email:[/] {record.email}")
        else:
            node.add("✉️  [cyan]Email:[/] [dim]not available[/]")

    # grouped
    if is_grouped:
        for group_name in book.keys():
            group_contacts: dict = book[group_name]
            group_node = tree.add(f"📂 [bold yellow]{group_name}[/]")

            if not group_contacts:
                group_node.add("[dim]No contacts[/]")
                continue

            for name in group_contacts.keys():
                record = group_contacts[name]
                add_contact_node(group_node, record)

    # ungrouped
    else:
        for name in book.keys():
            record = book[name]
            add_contact_node(tree, record)

    return tree

@inject
@handle_service_errors
def _all_impl(
    sort_by: Optional[ContactSortBy] = None,
    group: Optional[str] = "all",
    service: ContactService = Provide[Container.contact_service],
):
    if not service.has_contacts():
        console.print("[yellow]Address book is empty.[/yellow]")
        return

    all_contacts = service.get_all_contacts(sort_by=sort_by, group=group)
    console.print(show_address_book(all_contacts))

@app.command(name="all")
def all_command(
    sort_by: Optional[ContactSortBy] = typer.Option(
        None,
        "--sort-by",
        help="Sort by: name, phone, birthday, tag_count or tag_name",
    ),
    group: Optional[str] = typer.Option(
        "all",
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