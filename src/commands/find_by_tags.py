"""
Find contacts that have ALL specified tags (AND).
Controller+View: parse args, call service, handle errors, print results.
"""

import typer
from typing import List
from dependency_injector.wiring import Provide, inject
from rich.console import Console
from rich.table import Table

from src.container import Container
from src.services.contact_service import ContactService
from src.utils.command_decorators import handle_service_errors
from src.utils.validators import split_tags_string, normalize_tag, is_valid_tag

app = typer.Typer()
console = Console()


@inject
@handle_service_errors
def _find_by_tags_impl(
    tokens: List[str],
    service: ContactService = Provide[Container.contact_service],
):
    # expand tokens: each token may be CSV (quotes supported)
    raw: List[str] = []
    tags = [normalize_tag(t) for t in raw if t]
    for tok in tokens:
        raw.extend(split_tags_string(tok))
    tags: List[str] = []
    for t in raw:
        n = normalize_tag(t)
        tags.append(n)

    result = service.find_by_tags_all(tags)
    if not result:
        console.print("[yellow]No contacts found[/yellow]")
        return

    table = Table(title="Contacts with ALL tags")
    table.add_column("Name", style="bold")
    table.add_column("Tags")
    for name, rec in result:
        table.add_row(name, ", ".join(rec.tags_list()))
    console.print(table)


@app.command(name="find-by-tags")
def find_by_tags_command(
    tokens: List[str] = typer.Argument(
        ..., 
        help='One or more tags or CSV chunks (quotes supported): ai ml "data,science"',
    ),
):
    """Find contacts that have ALL given tags (AND)."""
    return _find_by_tags_impl(tokens)
