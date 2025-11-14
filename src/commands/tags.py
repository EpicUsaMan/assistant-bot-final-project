"""
Tags commands — manage tags for a contact.

Commands act as Controller + View:
- get user input, call service, handle errors, print results.
"""

import typer
from dependency_injector.wiring import Provide, inject
from rich.console import Console
from typing import List
from pathlib import Path
from src.container import Container
from src.services.contact_service import ContactService
from src.utils.command_decorators import auto_save, handle_service_errors
from src.utils.validators import validate_tag, split_tags_string, normalize_tag, is_valid_tag
from src.utils.paths import get_storage_path

app = typer.Typer()
console = Console()


@inject
@handle_service_errors
@auto_save
def _tag_add_impl(
    name: str,
    tags: list[str],
    service: ContactService = Provide[Container.contact_service],
    filename: Path = Provide[Container.config.storage.filename], 
):
    added = []
    for t in tags:
        n = normalize_tag(t)
        if not is_valid_tag(n):
            raise ValueError(f"Invalid tag: '{t}'")
        service.add_tag(name, n)
        added.append(n)

    console.print(f"[bold green]Tags added to {name}: {', '.join(added)}[/bold green]")

@app.command(name="tag-add")
def tag_add_command(
    name: str = typer.Argument(..., help="Contact name"),
    tags_tokens: List[str] = typer.Argument(
        ...,  
        help='One or more tags or CSV chunks (quotes supported): ml "data,science",ai',
        metavar="TAGS...",
    ),
    filename: Path = typer.Option(get_storage_path(), hidden=True)
):
    """Add one or many tags to a contact."""
    flat: List[str] = []
    for tok in tags_tokens:
        flat.extend(split_tags_string(tok))
    return _tag_add_impl(name, flat, filename=filename)

@inject
@handle_service_errors
@auto_save
def _tag_remove_impl(
    name: str,
    tag: str,
    service: ContactService = Provide[Container.contact_service],
    filename: Path = Provide[Container.config.storage.filename], 
):
    msg = service.remove_tag(name, tag)
    console.print(f"[bold green]{msg}[/bold green]")


@app.command(name="tag-remove")
def tag_remove_command(
    name: str = typer.Argument(..., help="Contact name"),
    tag: str = typer.Argument(..., help="Tag", callback=validate_tag),
    filename: Path = typer.Option(get_storage_path(), hidden=True),
):
    """Remove a tag from a contact."""
    return _tag_remove_impl(name, tag, filename=filename)


@inject
@handle_service_errors
@auto_save
def _tag_clear_impl(
    name: str,
    service: ContactService = Provide[Container.contact_service],
    filename: Path = Provide[Container.config.storage.filename], 
):
    msg = service.clear_tags(name)
    console.print(f"[bold green]{msg}[/bold green]")


@app.command(name="tag-clear")
def tag_clear_command(
    name: str = typer.Argument(..., help="Contact name"),
    filename: Path = typer.Option(get_storage_path(), hidden=True)
):
    """Clear all tags for a contact."""
    return _tag_clear_impl(name, filename=filename)


@inject
@handle_service_errors
def _tag_list_impl(
    name: str,
    service: ContactService = Provide[Container.contact_service],
):
    tags = service.list_tags(name)
    console.print(", ".join(tags) if tags else "(no tags)")


@app.command(name="tag-list")
def tag_list_command(
    name: str = typer.Argument(..., help="Contact name"),
):
    """List tags of a contact."""
    return _tag_list_impl(name)
