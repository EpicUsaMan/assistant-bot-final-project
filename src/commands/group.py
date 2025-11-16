"""
Unified group commands with subcommands.

All group-related operations organized under 'group' command:
- group list
- group add
- group use
- group show
- group rename
- group remove
"""

from typing import Optional

import typer
from dependency_injector.wiring import inject, Provide
from rich.console import Console
from rich.tree import Tree

from src.container import Container
from src.services.contact_service import ContactService
from src.utils.command_decorators import handle_service_errors, auto_save
from src.utils.progressive_params import progressive_params, TextInput

app = typer.Typer(
    help="Manage contact groups",
    invoke_without_command=True
)
console = Console()


# ============================================================================
# Group Commands
# ============================================================================

@inject
@handle_service_errors
def _group_list_impl(
    service: ContactService = Provide[Container.contact_service],
):
    """Implementation: List all contact groups."""
    groups = service.list_groups()
    current = service.get_current_group()

    if not groups:
        console.print("[yellow]No groups defined.[/yellow]")
        return

    tree = Tree("[bold cyan]Groups[/bold cyan]", guide_style="cyan")
    
    for group_id, count in groups:
        is_current = group_id == current
        if is_current:
            group_branch = tree.add(f"[bold green]{group_id}[/bold green] [green](current)[/green]")
        else:
            group_branch = tree.add(f"[cyan]{group_id}[/cyan]")
        
        group_branch.add(f"[white]Contacts: {count}[/white]")

    console.print(tree)


@app.command(name="list")
def group_list_command():
    """
    List all contact groups.
    
    Shows all groups with contact counts and indicates the current active group.
    
    Examples:
        group list
    """
    return _group_list_impl()


@inject
@handle_service_errors
@auto_save
def _group_add_impl(
    group_id: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Create a new contact group."""
    service.add_group(group_id)
    console.print(f"[green]Group '{group_id}' created.[/green]")


@app.command(name="add")
@progressive_params(
    group_id=TextInput("Group identifier (e.g. work, personal)", required=True)
)
def group_add_command(
    group_id: Optional[str] = typer.Argument(None, help="Group identifier, e.g. work, personal"),
):
    """
    Create a new contact group.
    
    Examples:
        group add work
        group add personal
    """
    return _group_add_impl(group_id=group_id)


@inject
@handle_service_errors
@auto_save
def _group_use_impl(
    group_id: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Switch active contact group."""
    service.set_current_group(group_id)
    console.print(f"[cyan]Current group set to '{group_id}'.[/cyan]")


@app.command(name="use")
@progressive_params(
    group_id=Container.group_selector_factory
)
def group_use_command(
    group_id: Optional[str] = typer.Argument(None, help="Group to activate"),
):
    """
    Switch active contact group.
    
    Examples:
        group use work
        group use personal
    """
    return _group_use_impl(group_id=group_id)


@inject
@handle_service_errors
def _group_show_impl(
    group_id: str,
    service: ContactService = Provide[Container.contact_service],
):
    """Implementation: Show details about a specific group."""
    groups = service.list_groups()
    current = service.get_current_group()
    
    # Find the group
    group_info = None
    for gid, count in groups:
        if gid == group_id:
            group_info = (gid, count)
            break
    
    if not group_info:
        console.print(f"[red]Group '{group_id}' not found.[/red]")
        return
    
    gid, count = group_info
    is_current = gid == current
    
    # Display group details using Tree view
    tree = Tree(f"[bold cyan]Group: {gid}[/bold cyan]", guide_style="cyan")
    
    tree.add(f"[cyan]Group ID:[/cyan] [white]{gid}[/white]")
    tree.add(f"[cyan]Contacts:[/cyan] [white]{count}[/white]")
    tree.add(f"[cyan]Current:[/cyan] [{'green]Yes[/green]' if is_current else 'white]No[/white]'}")
    
    console.print(tree)


@app.command(name="show")
@progressive_params(
    group_id=Container.group_selector_factory
)
def group_show_command(
    group_id: Optional[str] = typer.Argument(None, help="Group identifier to show"),
):
    """
    Show details about a specific group.
    
    Examples:
        group show work
        group show personal
    """
    return _group_show_impl(group_id=group_id)


@inject
@handle_service_errors
@auto_save
def _group_rename_impl(
    old_id: str,
    new_id: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Rename a contact group."""
    msg = service.rename_group(old_id, new_id)
    console.print(f"[green]{msg}[/green]")


@app.command(name="rename")
@progressive_params(
    old_id=Container.group_selector_factory,
    new_id=TextInput("New group identifier", required=True)
)
def group_rename_command(
    old_id: Optional[str] = typer.Argument(None, help="Existing group id"),
    new_id: Optional[str] = typer.Argument(None, help="New group id"),
):
    """
    Rename a contact group.
    
    Examples:
        group rename work office
        group rename temp archive
    """
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
    """Implementation: Remove a contact group."""
    msg = service.remove_group(group_id, force=force)
    console.print(f"[yellow]{msg}[/yellow]")


@app.command(name="remove")
@progressive_params(
    group_id=Container.group_selector_factory
)
def group_remove_command(
    group_id: Optional[str] = typer.Argument(None, help="Group id to remove"),
    force: bool = typer.Option(
        False,
        "--force",
        help="Remove group even if it has contacts",
    ),
):
    """
    Remove a contact group (optionally with its contacts).
    
    Examples:
        group remove temp
        group remove old --force
    """
    return _group_remove_impl(group_id=group_id, force=force)


# ============================================================================
# Interactive Menu
# ============================================================================

@app.callback(invoke_without_command=True)
def group_callback(ctx: typer.Context):
    """
    Callback for group command group.
    
    If no subcommand is provided, shows the list of groups.
    """
    if ctx.invoked_subcommand is None:
        return _group_list_impl()
