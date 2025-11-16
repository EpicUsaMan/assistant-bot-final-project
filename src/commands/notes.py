"""
Unified notes commands with subcommands.

All note-related operations organized under 'notes' command:
- notes add
- notes edit
- notes remove
- notes list
- notes show
- notes tag add
- notes tag remove
- notes tag clear
- notes tag list
"""

import typer
from typing import List, Optional
from functools import partial
from dependency_injector.wiring import Provide, inject
from rich.console import Console
from rich.tree import Tree

from src.container import Container
from src.services.note_service import NoteService
# Import container instance for progressive_params factories
from src.main import container
from src.utils.command_decorators import auto_save, handle_service_errors
from src.utils.validators import split_tags_string, normalize_tag, is_valid_tag
from src.utils.autocomplete import complete_contact_name, complete_note_name, complete_tag
from src.utils.progressive_params import progressive_params
from src.utils.interactive_menu import auto_menu, menu_command_map

app = typer.Typer(
    help="Manage notes for contacts",
    invoke_without_command=True
)
console = Console()


# ============================================================================
# Basic Note Commands
# ============================================================================

@progressive_params(
    contact_name=Container.contact_selector_factory,
    note_name=partial(Container.text_input_factory, "Note name/title", required=True),
    content=partial(Container.text_input_factory, "Note content", required=True, default="")
)
@inject
@handle_service_errors
@auto_save
def _add_note_impl(
    contact_name: str,
    note_name: str,
    content: str,
    service: NoteService = Provide[Container.note_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Add a note to a contact."""
    msg = service.add_note(contact_name, note_name, content)
    console.print(f"[bold green]{msg}[/bold green]")


@app.command(name="add")
def add_note_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
    note_name: Optional[str] = typer.Argument(None, help="Note name/title"),
    content: Optional[str] = typer.Argument(None, help="Note content"),
):
    """
    Add a note to a contact.
    
    Interactive prompts will guide you for any missing parameters.
    
    Examples:
        notes add                              # Fully interactive
        notes add "John"                       # Prompt for note name & content
        notes add "John" "Meeting"             # Prompt for content only
        notes add "John" "Meeting" "Content"   # Direct execution
    """
    return _add_note_impl(contact_name, note_name, content)


@inject
@handle_service_errors
@auto_save
def _edit_note_impl(
    contact_name: str,
    note_name: str,
    content: str,
    service: NoteService = Provide[Container.note_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Edit an existing note's content."""
    msg = service.edit_note(contact_name, note_name, content)
    console.print(f"[bold green]{msg}[/bold green]")


@app.command(name="edit")
@progressive_params(
    contact_name=Container.contact_selector_factory,
    note_name=Container.note_selector_factory,
    content=partial(Container.text_input_factory, "New content", required=True)
)
def edit_note_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
    note_name: Optional[str] = typer.Argument(None, help="Note name", autocompletion=complete_note_name),
    content: Optional[str] = typer.Argument(None, help="New note content"),
):
    """
    Edit an existing note's content.
    
    Supports progressive fulfillment:
        notes edit                           # Full interactive
        notes edit "John"                    # Select note, prompt content
        notes edit "John" "Meeting"          # Prompt content only
        notes edit "John" "Meeting" "New"    # Direct execution
    """
    return _edit_note_impl(contact_name, note_name, content)


@inject
@handle_service_errors
@auto_save
def _remove_note_impl(
    contact_name: str,
    note_name: str,
    service: NoteService = Provide[Container.note_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Remove a note from a contact."""
    msg = service.delete_note(contact_name, note_name)
    console.print(f"[bold green]{msg}[/bold green]")


@app.command(name="remove")
@progressive_params(
    contact_name=Container.contact_selector_factory,
    note_name=Container.note_selector_factory
)
def remove_note_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
    note_name: Optional[str] = typer.Argument(None, help="Note name", autocompletion=complete_note_name),
):
    """
    Remove a note from a contact.
    
    Supports progressive fulfillment:
        notes remove                         # Interactive contact + note selection
        notes remove "John"                  # Select note
        notes remove "John" "Meeting"        # Direct removal
    """
    return _remove_note_impl(contact_name, note_name)


@inject
@handle_service_errors
def _list_notes_impl(
    contact_name: str,
    service: NoteService = Provide[Container.note_service],
):
    """Implementation: List all notes for a contact."""
    notes = service.list_notes(contact_name)
    
    if not notes:
        console.print(f"[yellow]No notes for contact '{contact_name}'.[/yellow]")
        return
    
    tree = Tree(
        f"[bold cyan]📝 Notes for {contact_name}[/bold cyan]",
        guide_style="cyan"
    )
    
    for note in notes:
        note_branch = tree.add(f"[bold green]📄 {note.name}[/bold green]")
        
        if note.content:
            content_preview = (note.content[:60] + "...") if len(note.content) > 60 else note.content
            note_branch.add(f"[white]Content: {content_preview}[/white]")
        else:
            note_branch.add("[dim]Content: (empty)[/dim]")
        
        if note.tags_list():
            tags_str = ", ".join(note.tags_list())
            note_branch.add(f"[magenta]🏷️  Tags: {tags_str}[/magenta]")
    
    console.print(tree)


@app.command(name="list")
@progressive_params(
    contact_name=Container.contact_selector_factory
)
def list_notes_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
):
    """
    List all notes for a contact.
    
    Supports progressive fulfillment:
        notes list               # Interactive contact selection
        notes list "John"        # Direct listing
    """
    return _list_notes_impl(contact_name)


@inject
@handle_service_errors
def _show_note_impl(
    contact_name: str,
    note_name: str,
    service: NoteService = Provide[Container.note_service],
):
    """Implementation: Show full content of a specific note."""
    note = service.get_note(contact_name, note_name)
    
    tree = Tree(
        f"[bold cyan]📄 Note: {note.name}[/bold cyan] (Contact: {contact_name})",
        guide_style="cyan"
    )
    
    if note.content:
        content_branch = tree.add("[bold]📝 Content:[/bold]")
        lines = note.content.split('\n')
        for line in lines[:10]:
            content_branch.add(f"[white]{line}[/white]")
        if len(lines) > 10:
            content_branch.add(f"[dim]... and {len(lines) - 10} more lines[/dim]")
    else:
        tree.add("[dim]📝 Content: (empty)[/dim]")
    
    if note.tags_list():
        tags_branch = tree.add("[bold]🏷️  Tags:[/bold]")
        for tag in note.tags_list():
            tags_branch.add(f"[magenta]• {tag}[/magenta]")
    else:
        tree.add("[dim]🏷️  Tags: (none)[/dim]")
    
    console.print(tree)


@app.command(name="show")
@progressive_params(
    contact_name=Container.contact_selector_factory,
    note_name=Container.note_selector_factory
)
def show_note_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
    note_name: Optional[str] = typer.Argument(None, help="Note name", autocompletion=complete_note_name),
):
    """
    Show full content of a specific note.
    
    Supports progressive fulfillment:
        notes show                           # Full interactive
        notes show "John"                    # Select note
        notes show "John" "Meeting"          # Direct display
    """
    return _show_note_impl(contact_name, note_name)


# ============================================================================
# Tag Management Commands
# ============================================================================

tag_app = typer.Typer(
    help="Manage tags for notes",
    invoke_without_command=True
)


@progressive_params(
    contact_name=Container.contact_selector_factory,
    note_name=Container.note_selector_factory,
    tags=partial(Container.tags_input_factory, "Enter tags (comma-separated)", required=True)
)
@inject
@handle_service_errors
@auto_save
def _note_tag_add_impl(
    contact_name: str,
    note_name: str,
    tags: Optional[List[str]],
    service: NoteService = Provide[Container.note_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Add tags to a note."""
    if not tags:
        console.print("[yellow]No tags provided.[/yellow]")
        return
    
    added = []
    for tag in tags:
        normalized = normalize_tag(tag)
        if not is_valid_tag(normalized):
            raise ValueError(f"Invalid tag: '{tag}'")
        service.note_add_tag(contact_name, note_name, normalized)
        added.append(normalized)
    
    console.print(f"[bold green]Tags added to note '{note_name}': {', '.join(added)}[/bold green]")


@tag_app.command(name="add")
def note_tag_add_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
    note_name: Optional[str] = typer.Argument(None, help="Note name", autocompletion=complete_note_name),
    tags_tokens: Optional[List[str]] = typer.Argument(
        None,
        help='One or more tags or CSV chunks (quotes supported): important "to-do,urgent"',
        metavar="TAGS...",
        autocompletion=complete_tag,
    ),
):
    """
    Add one or many tags to a note.
    
    Supports progressive fulfillment:
        notes tag add                                # Full interactive
        notes tag add "John"                         # Select note, prompt tags
        notes tag add "John" "Meeting"               # Prompt tags
        notes tag add "John" "Meeting" work urgent   # Direct add
    """
    # Parse tags (handle both list and individual tokens)
    flat: Optional[List[str]] = None
    if tags_tokens is not None:
        flat = []
        if isinstance(tags_tokens, list):
            for token in tags_tokens:
                flat.extend(split_tags_string(token))
        else:
            flat.extend(split_tags_string(tags_tokens))
    
    return _note_tag_add_impl(contact_name, note_name, flat)


@progressive_params(
    contact_name=Container.contact_selector_factory,
    note_name=Container.note_selector_factory,
    tag=partial(Container.tag_selector_factory, "Select tag to remove")
)
@inject
@handle_service_errors
@auto_save
def _note_tag_remove_impl(
    contact_name: str,
    note_name: str,
    tag: str,
    service: NoteService = Provide[Container.note_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Remove a tag from a note."""
    msg = service.note_remove_tag(contact_name, note_name, tag)
    console.print(f"[bold green]{msg}[/bold green]")


@tag_app.command(name="remove")
def note_tag_remove_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
    note_name: Optional[str] = typer.Argument(None, help="Note name", autocompletion=complete_note_name),
    tag: Optional[str] = typer.Argument(None, help="Tag", autocompletion=complete_tag),
):
    """
    Remove a tag from a note.
    
    Supports progressive fulfillment:
        notes tag remove                         # Full interactive
        notes tag remove "John"                  # Select note and tag
        notes tag remove "John" "Meeting"        # Select tag
        notes tag remove "John" "Meeting" work   # Direct removal
    """
    return _note_tag_remove_impl(contact_name, note_name, tag)


@progressive_params(
    contact_name=Container.contact_selector_factory,
    note_name=Container.note_selector_factory
)
@inject
@handle_service_errors
@auto_save
def _note_tag_clear_impl(
    contact_name: str,
    note_name: str,
    service: NoteService = Provide[Container.note_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Clear all tags from a note."""
    msg = service.note_clear_tags(contact_name, note_name)
    console.print(f"[bold green]{msg}[/bold green]")


@tag_app.command(name="clear")
def note_tag_clear_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
    note_name: Optional[str] = typer.Argument(None, help="Note name", autocompletion=complete_note_name),
):
    """
    Clear all tags from a note.
    
    Supports progressive fulfillment:
        notes tag clear                         # Full interactive
        notes tag clear "John"                  # Select note
        notes tag clear "John" "Meeting"        # Direct clear
    """
    return _note_tag_clear_impl(contact_name, note_name)


@progressive_params(
    contact_name=Container.contact_selector_factory,
    note_name=Container.note_selector_factory
)
@inject
@handle_service_errors
def _note_tag_list_impl(
    contact_name: str,
    note_name: str,
    service: NoteService = Provide[Container.note_service],
):
    """Implementation: List tags of a note."""
    tags = service.note_list_tags(contact_name, note_name)
    console.print(", ".join(tags) if tags else "(no tags)")


@tag_app.command(name="list")
def note_tag_list_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
    note_name: Optional[str] = typer.Argument(None, help="Note name", autocompletion=complete_note_name),
):
    """
    List tags of a note.
    
    Supports progressive fulfillment:
        notes tag list                         # Full interactive
        notes tag list "John"                  # Select note
        notes tag list "John" "Meeting"        # Direct listing
    """
    return _note_tag_list_impl(contact_name, note_name)


@tag_app.callback(invoke_without_command=True)
def tag_callback(ctx: typer.Context):
    """Callback for tag command group. Shows menu if no subcommand."""
    if ctx.invoked_subcommand is None:
        return _manage_note_tags_submenu()


# Register tag sub-app
app.add_typer(tag_app, name="tag")


# ============================================================================
# Interactive Menu
# ============================================================================

def _notes_menu():
    """
    Interactive notes management menu using generic auto_menu framework.
    
    The menu is generated automatically and calls commands with None parameters.
    Progressive params handles all the interactive prompting.
    """
    # Define main menu commands
    main_commands = menu_command_map(
        ("add", add_note_command, "Add note", (None, None, None)),
        ("list", list_notes_command, "List notes", (None,)),
        ("show", show_note_command, "Show note (full content)", (None, None)),
        ("edit", edit_note_command, "Edit note", (None, None, None)),
        ("remove", remove_note_command, "Remove note", (None, None)),
        ("tags", _manage_note_tags_submenu, "Manage note tags", ()),
    )
    
    # Use generic auto_menu
    auto_menu(None, title="Notes Management Menu", commands=main_commands)


def _manage_note_tags_submenu():
    """Sub-menu for tag management using generic auto_menu framework."""
    # Define tag menu commands
    tag_commands = menu_command_map(
        ("add", note_tag_add_command, "Add tags", (None, None, None)),
        ("remove", note_tag_remove_command, "Remove tag", (None, None, None)),
        ("clear", note_tag_clear_command, "Clear all tags", (None, None)),
        ("list", note_tag_list_command, "List tags", (None, None)),
    )
    
    # Use generic auto_menu
    auto_menu(None, title="Tag Management", commands=tag_commands)


@app.callback(invoke_without_command=True)
def notes_callback(ctx: typer.Context):
    """
    Callback for notes command group.
    
    If no subcommand is provided, launches the interactive menu.
    """
    if ctx.invoked_subcommand is None:
        return _notes_menu()

