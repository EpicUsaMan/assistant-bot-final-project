"""
Unified search commands with subcommands.

All search-related operations organized under 'search' command:
- search menu (interactive)
- search contacts
- search notes
"""

import typer
from typing import Optional
from functools import partial
from dependency_injector.wiring import Provide, inject
from rich.console import Console
from rich.tree import Tree

from src.container import Container
from src.services.search_service import (
    SearchService, 
    ContactSearchType, 
    NoteSearchType
)
from src.utils.command_decorators import handle_service_errors
from src.utils.progressive_params import progressive_params
from src.utils.interactive_menu import auto_menu, menu_command_map

app = typer.Typer(
    help="Search contacts and notes",
    invoke_without_command=True
)
console = Console()


# ============================================================================
# Helper Functions for Display
# ============================================================================

def display_contact_results_tree(results, query: str, search_type: str):
    """Display contact search results in a tree view."""
    if not results:
        console.print(f"[yellow]No contacts found matching '{query}' in {search_type}.[/yellow]")
        return
    
    tree = Tree(
        f"[bold cyan]🔍 Found {len(results)} contact(s)[/bold cyan] - '{query}' in {search_type}",
        guide_style="cyan"
    )
    
    for name, record in results:
        contact_branch = tree.add(f"[bold green]📇 {name}[/bold green]")
        
        if record.phones:
            phones_str = ", ".join(p.value for p in record.phones)
            contact_branch.add(f"[white]📱 Phones: {phones_str}[/white]")
        
        if record.birthday:
            contact_branch.add(f"[blue]🎂 Birthday: {record.birthday}[/blue]")
        
        if hasattr(record, 'email') and record.email:
            contact_branch.add(f"[cyan]📧 Email: {record.email}[/cyan]")
        
        if record.tags_list():
            tags_str = ", ".join(record.tags_list())
            contact_branch.add(f"[magenta]🏷️  Tags: {tags_str}[/magenta]")
        
        notes = record.list_notes()
        if notes:
            notes_branch = contact_branch.add(f"[yellow]📝 Notes: {len(notes)}[/yellow]")
            for note in notes[:3]:
                content_preview = (note.content[:30] + "...") if len(note.content) > 30 else note.content
                notes_branch.add(f"[dim]• {note.name}: {content_preview}[/dim]")
            if len(notes) > 3:
                notes_branch.add(f"[dim]... and {len(notes) - 3} more[/dim]")
        else:
            contact_branch.add("[dim]📝 Notes: 0[/dim]")
    
    console.print(tree)


def display_note_results_tree(results, query: str, search_type: str):
    """Display note search results in a tree view."""
    if not results:
        console.print(f"[yellow]No notes found matching '{query}' in {search_type}.[/yellow]")
        return
    
    tree = Tree(
        f"[bold cyan]🔍 Found {len(results)} note(s)[/bold cyan] - '{query}' in {search_type}",
        guide_style="cyan"
    )
    
    notes_by_contact = {}
    for contact_name, note_name, note in results:
        if contact_name not in notes_by_contact:
            notes_by_contact[contact_name] = []
        notes_by_contact[contact_name].append((note_name, note))
    
    for contact_name, notes in notes_by_contact.items():
        contact_branch = tree.add(f"[bold green]📇 {contact_name}[/bold green]")
        
        for note_name, note in notes:
            note_branch = contact_branch.add(f"[bold cyan]📄 {note_name}[/bold cyan]")
            
            if note.content:
                content_preview = (note.content[:60] + "...") if len(note.content) > 60 else note.content
                note_branch.add(f"[white]Content: {content_preview}[/white]")
            else:
                note_branch.add("[dim]Content: (empty)[/dim]")
            
            if note.tags_list():
                tags_str = ", ".join(note.tags_list())
                note_branch.add(f"[magenta]🏷️  Tags: {tags_str}[/magenta]")
    
    console.print(tree)


# ============================================================================
# Search Contacts Command
# ============================================================================

def _get_contact_search_type_choices():
    """Get choices for contact search type selection."""
    return [
        ("all", "All fields (comprehensive search)"),
        ("name", "Contact name"),
        ("phone", "Phone number"),
        ("tags", "Tags (substring)"),
        ("tags-all", "All tags (AND)"),
        ("tags-any", "Any tag (OR)"),
        ("notes-text", "Note content"),
        ("notes-name", "Note names"),
        ("notes-tags", "Note tags"),
    ]


@inject
@handle_service_errors
def _search_contacts_impl(
    query: str,
    by: str,
    service: SearchService = Provide[Container.search_service],
):
    """Implementation: Search contacts by various criteria."""
    try:
        search_type = ContactSearchType(by)
    except ValueError:
        valid_types = ", ".join([t.value for t in ContactSearchType])
        console.print(f"[red]Invalid search type '{by}'. Valid types: {valid_types}[/red]")
        raise typer.Exit(1)
    
    results = service.search_contacts(query, search_type)
    display_contact_results_tree(results, query, by)


@app.command(name="contacts")
@progressive_params(
    query=partial(Container.text_input_factory, "Enter search query:", required=True),
    by=partial(Container.select_input_factory, "Select search type:", choices=_get_contact_search_type_choices(), required=False)
)
def search_contacts_command(
    query: Optional[str] = typer.Argument(None, help="Search query (for tags-all/tags-any use comma-separated: work,important)"),
    by: Optional[str] = typer.Option(
        "all",
        "--by",
        help="Search type: all, name, phone, tags, tags-all, tags-any, notes-text, notes-name, notes-tags"
    ),
):
    """
    Search for contacts by various criteria.
    
    Interactive prompts will guide you for any missing parameters.
    
    Examples:
    
        search contacts                              # Fully interactive
        search contacts "john"                       # Search everywhere
        search contacts "john" --by=name             # Search by name
        search contacts --by=name "john"             # Also works
        search contacts "1234" --by=phone
        search contacts "meeting" --by=notes-text
        search contacts "important" --by=tags
        search contacts "work,important" --by=tags-all
        search contacts "personal,work" --by=tags-any
    """
    return _search_contacts_impl(query, by)


# ============================================================================
# Search Notes Command
# ============================================================================

def _get_note_search_type_choices():
    """Get choices for note search type selection."""
    return [
        ("all", "All fields (comprehensive search)"),
        ("name", "Note name"),
        ("text", "Note content"),
        ("tags", "Note tags"),
        ("contact-name", "Contact name"),
        ("contact-phone", "Contact phone"),
        ("contact-tags", "Contact tags"),
    ]


@inject
@handle_service_errors
def _search_notes_impl(
    query: str,
    by: str,
    service: SearchService = Provide[Container.search_service],
):
    """Implementation: Search notes by various criteria."""
    try:
        search_type = NoteSearchType(by)
    except ValueError:
        valid_types = ", ".join([t.value for t in NoteSearchType])
        console.print(f"[red]Invalid search type '{by}'. Valid types: {valid_types}[/red]")
        raise typer.Exit(1)
    
    results = service.search_notes(query, search_type)
    display_note_results_tree(results, query, by)


@app.command(name="notes")
@progressive_params(
    query=partial(Container.text_input_factory, "Enter search query:", required=True),
    by=partial(Container.select_input_factory, "Select search type:", choices=_get_note_search_type_choices(), required=False)
)
def search_notes_command(
    query: Optional[str] = typer.Argument(None, help="Search query"),
    by: Optional[str] = typer.Option(
        "all",
        "--by",
        help="Search type: all, name, text, tags, contact-name, contact-phone, contact-tags"
    ),
):
    """
    Search for notes by various criteria.
    
    Interactive prompts will guide you for any missing parameters.
    
    Examples:
    
        search notes                           # Fully interactive
        search notes "meeting"                 # Search everywhere
        search notes "meeting" --by=name       # Search note names
        search notes --by=name "meeting"       # Also works
        search notes "discuss targets" --by=text
        search notes "john" --by=contact-name
        search notes "important" --by=tags
    """
    return _search_notes_impl(query, by)


# ============================================================================
# Interactive Menu Command
# ============================================================================

def _search_menu():
    """
    Interactive search menu using generic auto_menu framework.
    
    The menu is generated automatically and calls commands with None parameters.
    Progressive params handles all the interactive prompting.
    """
    # Define search menu commands
    search_commands = menu_command_map(
        ("contacts", search_contacts_command, "Search contacts", (None, None)),
        ("notes", search_notes_command, "Search notes", (None, None)),
    )
    
    # Use generic auto_menu
    auto_menu(None, title="Interactive Search", commands=search_commands)


@app.callback(invoke_without_command=True)
def search_callback(ctx: typer.Context):
    """
    Callback for search command group.
    
    If no subcommand is provided, launches the interactive menu.
    """
    if ctx.invoked_subcommand is None:
        return _search_menu()
