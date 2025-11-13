"""Group commands - manage contact groups."""

from typing import Optional

import typer
from dependency_injector.wiring import inject, Provide
from rich.console import Console
from rich.table import Table

from src.container import Container
from src.services.contact_service import ContactService
from src.utils.command_decorators import handle_service_errors, auto_save

app = typer.Typer()
console = Console()


# --- list groups ---

@inject
@handle_service_errors
def _group_list_impl(
    service: ContactService = Provide[Container.contact_service],
):
    groups = service.list_groups()
    current = service.get_current_group()

    if not groups:
        console.print("[yellow]No groups defined.[/yellow]")
        return

    table = Table(title="Groups")
    table.add_column("Group ID", style="cyan", no_wrap=True)
    table.add_column("Contacts", style="magenta")
    table.add_column("Current", style="green")

    for group_id, count in groups:
        marker = "●" if group_id == current else ""
        table.add_row(group_id, str(count), marker)

    console.print(table)


@app.command(name="group-list")
def group_list_command():
    """List all contact groups."""
    return _group_list_impl()


# --- add group ---

@inject
@handle_service_errors
@auto_save
def _group_add_impl(
    group_id: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    service.add_group(group_id)
    console.print(f"[green]Group '{group_id}' created.[/green]")


@app.command(name="group-add")
def group_add_command(
    group_id: str = typer.Argument(..., help="Group identifier, e.g. work, personal"),
):
    """Create a new contact group."""
    return _group_add_impl(group_id=group_id)


# --- use group ---

@inject
@handle_service_errors
@auto_save  # чтобы выбор группы сохранялся вместе с книгой
def _group_use_impl(
    group_id: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    service.set_current_group(group_id)
    console.print(f"[cyan]Current group set to '{group_id}'.[/cyan]")


@app.command(name="group-use")
def group_use_command(
    group_id: str = typer.Argument(..., help="Group to activate"),
):
    """Switch active contact group."""
    return _group_use_impl(group_id=group_id)

@inject
@handle_service_errors
@auto_save
def _group_rename_impl(
    old_id: str,
    new_id: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    msg = service.rename_group(old_id, new_id)
    console.print(f"[green]{msg}[/green]")


@app.command(name="group-rename")
def group_rename_command(
    old_id: str = typer.Argument(..., help="Existing group id"),
    new_id: str = typer.Argument(..., help="New group id"),
):
    """Rename a contact group."""
    return _group_rename_impl(old_id=old_id, new_id=new_id)

@inject
@handle_service_errors
@auto_save
def _group_remove_impl(
    group_id: str,
    force: bool = False,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    msg = service.remove_group(group_id, force=force)
    console.print(f"[yellow]{msg}[/yellow]")


@app.command(name="group-remove")
def group_remove_command(
    group_id: str = typer.Argument(..., help="Group id to remove"),
    force: bool = typer.Option(
        False,
        "--force",
        help="Delete group even if it has contacts",
    ),
):
    """Remove a contact group (optionally with its contacts)."""
    return _group_remove_impl(group_id=group_id, force=force)
