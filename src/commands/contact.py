"""
Unified contact commands with nested subcommands.

All contact-related operations organized under 'contact' command:
- contact add
- contact remove
- contact show
- contact list
- contact phone add
- contact phone remove
- contact phone change
- contact phone list
- contact birthday add
- contact birthday show
- contact birthday upcoming
- contact tag add
- contact tag remove
- contact tag clear
- contact tag list
- contact email add
- contact email remove
- contact address set
- contact address remove
"""

import typer
from typing import List, Optional
from functools import partial
from dependency_injector.wiring import Provide, inject
from rich.console import Console
from rich.tree import Tree
from rich.table import Table

from src.container import Container
from src.services.contact_service import ContactService
from src.utils.command_decorators import auto_save, handle_service_errors
from src.utils.validators import (
    validate_phone,
    validate_birthday,
    validate_email,
    split_tags_string,
    normalize_tag,
    is_valid_tag,
)
from src.utils.autocomplete import complete_contact_name, complete_tag
from src.utils.progressive_params import progressive_params
from src.utils.interactive_menu import auto_menu, menu_command_map

app = typer.Typer(
    help="Manage contacts (add, remove, show)",
    invoke_without_command=True
)
console = Console()


# ============================================================================
# Basic Contact Commands
# ============================================================================

@inject
@handle_service_errors
@auto_save
def _add_contact_impl(
    name: str,
    phone: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Add a new contact with a phone number."""
    message = service.add_contact(name, phone)
    console.print(f"[bold green]{message}[/bold green]")


@app.command(name="add")
@progressive_params(
    contact_name=partial(Container.text_input_factory, "Contact name", required=True),
    phone=partial(Container.text_input_factory, "Phone number", required=True)
)
def add_contact_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name"),
    phone: Optional[str] = typer.Argument(None, help="Phone number (10 digits)"),
):
    """
    Add a new contact with a phone number.
    
    Fails if contact already exists. Use 'contact phone add' to add more phone numbers.
    
    Examples:
        contact add                              # Fully interactive
        contact add "John"                       # Prompt for phone
        contact add "John" "1234567890"          # Direct execution
    """
    # Validate phone if provided
    if phone is not None:
        phone = validate_phone(phone)
    return _add_contact_impl(contact_name, phone)


@inject
@handle_service_errors
@auto_save
def _edit_contact_impl(
    old_name: str,
    new_name: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Edit a contact's name."""
    message = service.edit_contact_name(old_name, new_name)
    console.print(f"[bold green]{message}[/bold green]")


@app.command(name="edit")
@progressive_params(
    old_name=Container.contact_selector_factory,
    new_name=partial(Container.text_input_factory, "New contact name", required=True)
)
def edit_contact_command(
    old_name: Optional[str] = typer.Argument(None, help="Current contact name", autocompletion=complete_contact_name),
    new_name: Optional[str] = typer.Argument(None, help="New contact name"),
):
    """
    Edit a contact's name.
    
    Fails if old contact doesn't exist or new name already exists.
    
    Examples:
        contact edit                             # Fully interactive
        contact edit "John"                      # Prompt for new name
        contact edit "John" "John Smith"         # Direct execution
    """
    return _edit_contact_impl(old_name, new_name)


@inject
@handle_service_errors
@auto_save
def _remove_contact_impl(
    name: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Remove a contact from the address book."""
    message = service.delete_contact(name)
    console.print(f"[bold green]{message}[/bold green]")


@app.command(name="remove")
@progressive_params(
    contact_name=Container.contact_selector_factory
)
def remove_contact_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
):
    """
    Remove a contact from the address book.
    
    Supports progressive fulfillment:
        contact remove                         # Interactive contact selection
        contact remove "John"                  # Direct removal
    """
    return _remove_contact_impl(contact_name)


@inject
@handle_service_errors
def _show_contact_impl(
    name: str,
    service: ContactService = Provide[Container.contact_service],
):
    """Implementation: Show detailed information about a contact."""
    record = service.get_contact(name)
    
    tree = Tree(
        f"[bold cyan]Contact: {record.name}[/bold cyan]",
        guide_style="cyan"
    )
    
    if record.phones:
        phones_branch = tree.add("[bold]Phones:[/bold]")
        for phone in record.phones:
            phones_branch.add(f"[green]{phone}[/green]")
    else:
        tree.add("[dim]Phones: (none)[/dim]")
    
    if record.birthday:
        tree.add(f"[bold]Birthday:[/bold] [yellow]{record.birthday}[/yellow]")
    else:
        tree.add("[dim]Birthday: (not set)[/dim]")
    
    if record.email:
        tree.add(f"[bold]Email:[/bold] [blue]{record.email}[/blue]")
    else:
        tree.add("[dim]Email: (not set)[/dim]")
    
    if record.address:
        addr_branch = tree.add("[bold]Address:[/bold]")
        addr_branch.add(f"[white]{record.address}[/white]")
    else:
        tree.add("[dim]Address: (not set)[/dim]")
    
    if record.tags_list():
        tags_branch = tree.add("[bold]Tags:[/bold]")
        for tag in record.tags_list():
            tags_branch.add(f"[magenta]{tag}[/magenta]")
    else:
        tree.add("[dim]Tags: (none)[/dim]")
    
    console.print(tree)


@app.command(name="show")
@progressive_params(
    contact_name=Container.contact_selector_factory
)
def show_contact_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
):
    """
    Show detailed information about a contact.
    
    Supports progressive fulfillment:
        contact show                         # Interactive contact selection
        contact show "John"                  # Direct display
    """
    return _show_contact_impl(contact_name)


@inject
@handle_service_errors
def _list_contacts_impl(
    sort_by: Optional[str] = None,
    group: Optional[str] = None,
    service: ContactService = Provide[Container.contact_service],
):
    """Implementation: List all contacts in the address book."""
    from src.services.contact_service import ContactSortBy
    
    # Convert string to ContactSortBy enum if provided
    sort_by_enum = None
    if sort_by:
        try:
            sort_by_enum = ContactSortBy(sort_by)
        except ValueError:
            console.print(f"[red]Invalid sort option: {sort_by}[/red]")
            console.print(f"[yellow]Valid options: {', '.join([e.value for e in ContactSortBy])}[/yellow]")
            return
    
    if not service.has_contacts():
        console.print("[yellow]Address book is empty.[/yellow]")
        return

    all_contacts = service.get_all_contacts(sort_by=sort_by_enum, group=group)
    
    # Get current group name for display
    current_group_id = service.get_current_group()
    group_obj = service.address_book.groups.get(current_group_id)
    group_name = group_obj.display_name if group_obj else current_group_id
    
    # Display contacts using tree view
    tree = _build_contacts_tree(all_contacts, group_name)
    console.print(tree)


def _build_contacts_tree(book: dict, group_name: str = "default") -> Tree:
    """Build a tree view of contacts."""
    tree = Tree(f"[bold cyan]Address Book ({group_name})[/]")
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


@app.command(name="list")
def list_contacts_command(
    sort_by: Optional[str] = typer.Option(
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
    List all contacts in the address book.
    
    Displays contacts with their details in a tree view. Can be sorted and filtered by group.
    
    Examples:
        contact list
        contact list --sort-by name
        contact list --sort-by birthday
        contact list --group all
        contact list --group work
    """
    return _list_contacts_impl(sort_by=sort_by, group=group)


# ============================================================================
# Phone Management Commands
# ============================================================================

phone_app = typer.Typer(
    help="Manage phone numbers for contacts",
    invoke_without_command=True
)


@inject
@handle_service_errors
@auto_save
def _phone_add_impl(
    name: str,
    phone: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Add a phone number to a contact."""
    message = service.add_contact(name, phone)
    console.print(f"[bold green]{message}[/bold green]")


@phone_app.command(name="add")
@progressive_params(
    contact_name=Container.contact_selector_factory,
    phone=partial(Container.text_input_factory, "Phone number", required=True)
)
def phone_add_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
    phone: Optional[str] = typer.Argument(None, help="Phone number (10 digits)"),
):
    """
    Add a phone number to a contact.
    
    Interactive prompts will guide you for any missing parameters.
    
    Examples:
        contact phone add                              # Fully interactive
        contact phone add "John"                       # Prompt for phone
        contact phone add "John" "1234567890"          # Direct execution
    """
    # Validate phone if provided
    if phone is not None:
        phone = validate_phone(phone)
    return _phone_add_impl(contact_name, phone)


@inject
@handle_service_errors
@auto_save
def _phone_remove_impl(
    name: str,
    phone: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Remove a phone number from a contact."""
    message = service.remove_phone(name, phone)
    console.print(f"[bold green]{message}[/bold green]")


@phone_app.command(name="remove")
@progressive_params(
    contact_name=Container.contact_selector_factory,
    phone=partial(Container.text_input_factory, "Phone number to remove", required=True)
)
def phone_remove_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
    phone: Optional[str] = typer.Argument(None, help="Phone number to remove"),
):
    """
    Remove a phone number from a contact.
    
    Note: Cannot remove the last phone number - contact must have at least one phone.
    
    Supports progressive fulfillment:
        contact phone remove                         # Full interactive
        contact phone remove "John"                  # Select phone to remove
        contact phone remove "John" "1234567890"     # Direct removal
    """
    # Validate phone if provided
    if phone is not None:
        phone = validate_phone(phone)
    return _phone_remove_impl(contact_name, phone)


@inject
@handle_service_errors
@auto_save
def _phone_change_impl(
    name: str,
    old_phone: str,
    new_phone: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Change an existing phone number."""
    message = service.change_contact(name, old_phone, new_phone)
    console.print(f"[bold green]{message}[/bold green]")


@phone_app.command(name="change")
@progressive_params(
    contact_name=Container.contact_selector_factory,
    old_phone=partial(Container.text_input_factory, "Old phone number", required=True),
    new_phone=partial(Container.text_input_factory, "New phone number", required=True)
)
def phone_change_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
    old_phone: Optional[str] = typer.Argument(None, help="Old phone number"),
    new_phone: Optional[str] = typer.Argument(None, help="New phone number"),
):
    """
    Change an existing phone number.
    
    Supports progressive fulfillment:
        contact phone change                                      # Full interactive
        contact phone change "John"                               # Select phone, prompt new
        contact phone change "John" "1234567890"                  # Prompt new phone
        contact phone change "John" "1234567890" "0987654321"     # Direct change
    """
    # Validate phones if provided
    if old_phone is not None:
        old_phone = validate_phone(old_phone)
    if new_phone is not None:
        new_phone = validate_phone(new_phone)
    return _phone_change_impl(contact_name, old_phone, new_phone)


@inject
@handle_service_errors
def _phone_list_impl(
    name: str,
    service: ContactService = Provide[Container.contact_service],
):
    """Implementation: List all phone numbers for a contact."""
    message = service.get_phone(name)
    console.print(f"[bold cyan]{message}[/bold cyan]")


@phone_app.command(name="edit")
@progressive_params(
    contact_name=Container.contact_selector_factory,
    old_phone=partial(Container.text_input_factory, "Phone number to edit", required=True),
    new_phone=partial(Container.text_input_factory, "New phone number", required=True)
)
def phone_edit_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
    old_phone: Optional[str] = typer.Argument(None, help="Phone number to edit"),
    new_phone: Optional[str] = typer.Argument(None, help="New phone number"),
):
    """
    Edit an existing phone number.
    
    Supports progressive fulfillment:
        contact phone edit                                      # Full interactive
        contact phone edit "John"                               # Select phone, prompt new
        contact phone edit "John" "1234567890"                  # Prompt new phone
        contact phone edit "John" "1234567890" "0987654321"     # Direct edit
    """
    # Validate phones if provided
    if old_phone is not None:
        old_phone = validate_phone(old_phone)
    if new_phone is not None:
        new_phone = validate_phone(new_phone)
    return _phone_change_impl(contact_name, old_phone, new_phone)


@phone_app.command(name="list")
@progressive_params(
    contact_name=Container.contact_selector_factory
)
def phone_list_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
):
    """
    List all phone numbers for a contact.
    
    Supports progressive fulfillment:
        contact phone list                         # Interactive contact selection
        contact phone list "John"                  # Direct listing
    """
    return _phone_list_impl(contact_name)


# ============================================================================
# Birthday Management Commands
# ============================================================================

birthday_app = typer.Typer(
    help="Manage birthdays for contacts",
    invoke_without_command=True
)


@inject
@handle_service_errors
@auto_save
def _birthday_add_impl(
    name: str,
    birthday: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Add a birthday to a contact."""
    message = service.add_birthday(name, birthday)
    console.print(f"[bold green]{message}[/bold green]")


@birthday_app.command(name="add")
@progressive_params(
    contact_name=Container.contact_selector_factory,
    birthday=partial(Container.text_input_factory, "Birthday (DD.MM.YYYY)", required=True)
)
def birthday_add_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
    birthday: Optional[str] = typer.Argument(None, help="Birthday in DD.MM.YYYY format"),
):
    """
    Add a birthday date to a contact.
    
    Interactive prompts will guide you for any missing parameters.
    
    Examples:
        contact birthday add                              # Fully interactive
        contact birthday add "John"                       # Prompt for birthday
        contact birthday add "John" "15.03.1990"          # Direct execution
    """
    # Validate birthday if provided
    if birthday is not None:
        birthday = validate_birthday(birthday)
    return _birthday_add_impl(contact_name, birthday)


@inject
@handle_service_errors
def _birthday_show_impl(
    name: str,
    service: ContactService = Provide[Container.contact_service],
):
    """Implementation: Show birthday for a contact."""
    message = service.get_birthday(name)
    console.print(f"[bold cyan]{message}[/bold cyan]")


@birthday_app.command(name="show")
@progressive_params(
    contact_name=Container.contact_selector_factory
)
def birthday_show_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
):
    """
    Show the birthday date for a contact.
    
    Supports progressive fulfillment:
        contact birthday show                         # Interactive contact selection
        contact birthday show "John"                  # Direct display
    """
    return _birthday_show_impl(contact_name)


@inject
@handle_service_errors
@auto_save
def _birthday_edit_impl(
    name: str,
    birthday: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Edit a birthday for a contact."""
    message = service.add_birthday(name, birthday)
    console.print(f"[bold green]{message}[/bold green]")


@birthday_app.command(name="edit")
@progressive_params(
    contact_name=Container.contact_selector_factory,
    birthday=partial(Container.text_input_factory, "New birthday (DD.MM.YYYY)", required=True)
)
def birthday_edit_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
    birthday: Optional[str] = typer.Argument(None, help="New birthday in DD.MM.YYYY format"),
):
    """
    Edit the birthday date for a contact.
    
    Updates an existing birthday or adds one if not set.
    
    Examples:
        contact birthday edit                              # Fully interactive
        contact birthday edit "John"                       # Prompt for new birthday
        contact birthday edit "John" "20.05.1995"          # Direct update
    """
    # Validate birthday if provided
    if birthday is not None:
        birthday = validate_birthday(birthday)
    return _birthday_edit_impl(contact_name, birthday)


@inject
@handle_service_errors
def _birthday_upcoming_impl(
    service: ContactService = Provide[Container.contact_service],
):
    """Implementation: Show upcoming birthdays for the next week."""
    from rich.panel import Panel
    
    message = service.get_upcoming_birthdays()
    
    if "No upcoming birthdays" in message:
        console.print(f"[yellow]{message}[/yellow]")
    else:
        console.print(
            Panel(
                message,
                title="[bold]Upcoming Birthdays[/bold]",
                border_style="magenta"
            )
        )


@birthday_app.command(name="upcoming")
def birthday_upcoming_command():
    """
    Show all upcoming birthdays for the next week.
    
    Displays birthdays occurring in the next 7 days with adjusted dates for weekends.
    
    Examples:
        contact birthday upcoming
    """
    return _birthday_upcoming_impl()


# ============================================================================
# Tag Management Commands
# ============================================================================

tag_app = typer.Typer(
    help="Manage tags for contacts",
    invoke_without_command=True
)


@inject
@handle_service_errors
@auto_save
def _tag_add_impl(
    name: str,
    tags: List[str],
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Add tags to a contact."""
    if not tags:
        console.print("[yellow]No tags provided.[/yellow]")
        return
    
    added = []
    for tag in tags:
        normalized = normalize_tag(tag)
        if not is_valid_tag(normalized):
            raise ValueError(f"Invalid tag: '{tag}'")
        service.add_tag(name, normalized)
        added.append(normalized)
    
    console.print(f"[bold green]Tags added to {name}: {', '.join(added)}[/bold green]")


@tag_app.command(name="add")
@progressive_params(
    contact_name=Container.contact_selector_factory,
    tags=partial(Container.tags_input_factory, "Enter tags (comma-separated)", required=True)
)
def tag_add_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
    tags: Optional[List[str]] = typer.Argument(
        None,
        help='One or more tags or CSV chunks (quotes supported): work "urgent,important"',
        metavar="TAGS...",
    ),
):
    """
    Add one or many tags to a contact.
    
    Supports progressive fulfillment:
        contact tag add                                # Full interactive
        contact tag add "John"                         # Prompt for tags
        contact tag add "John" work urgent             # Direct add
    """
    # Parse tags (handle both list and individual tokens)
    flat: Optional[List[str]] = None
    if tags is not None:
        flat = []
        if isinstance(tags, list):
            for token in tags:
                flat.extend(split_tags_string(token))
        else:
            flat.extend(split_tags_string(tags))
    
    return _tag_add_impl(contact_name, flat)


@inject
@handle_service_errors
@auto_save
def _tag_remove_impl(
    name: str,
    tag: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Remove a tag from a contact."""
    msg = service.remove_tag(name, tag)
    console.print(f"[bold green]{msg}[/bold green]")


@tag_app.command(name="remove")
@progressive_params(
    contact_name=Container.contact_selector_factory,
    tag=partial(Container.tag_selector_factory, "Select tag to remove")
)
def tag_remove_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
    tag: Optional[str] = typer.Argument(None, help="Tag", autocompletion=complete_tag),
):
    """
    Remove a tag from a contact.
    
    Supports progressive fulfillment:
        contact tag remove                         # Full interactive
        contact tag remove "John"                  # Select tag
        contact tag remove "John" work             # Direct removal
    """
    return _tag_remove_impl(contact_name, tag)


@inject
@handle_service_errors
@auto_save
def _tag_clear_impl(
    name: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Clear all tags from a contact."""
    msg = service.clear_tags(name)
    console.print(f"[bold green]{msg}[/bold green]")


@tag_app.command(name="clear")
@progressive_params(
    contact_name=Container.contact_selector_factory
)
def tag_clear_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
):
    """
    Clear all tags from a contact.
    
    Supports progressive fulfillment:
        contact tag clear                         # Interactive contact selection
        contact tag clear "John"                  # Direct clear
    """
    return _tag_clear_impl(contact_name)


@inject
@handle_service_errors
def _tag_list_impl(
    name: str,
    service: ContactService = Provide[Container.contact_service],
):
    """Implementation: List tags of a contact."""
    tags = service.list_tags(name)
    console.print(", ".join(tags) if tags else "(no tags)")


@tag_app.command(name="list")
@progressive_params(
    contact_name=Container.contact_selector_factory
)
def tag_list_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
):
    """
    List tags of a contact.
    
    Supports progressive fulfillment:
        contact tag list                         # Interactive contact selection
        contact tag list "John"                  # Direct listing
    """
    return _tag_list_impl(contact_name)


# ============================================================================
# Email Management Commands
# ============================================================================

email_app = typer.Typer(
    help="Manage email addresses for contacts",
    invoke_without_command=True
)


@inject
@handle_service_errors
@auto_save
def _email_add_impl(
    name: str,
    email: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Add or update email address for a contact."""
    message = service.add_email(name, email)
    console.print(f"[bold green]{message}[/bold green]")


@email_app.command(name="add")
@progressive_params(
    contact_name=Container.contact_selector_factory,
    email=partial(Container.email_input_factory, "Enter email address", required=True)
)
def email_add_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
    email: Optional[str] = typer.Argument(None, help="Email address"),
):
    """
    Add or update email address for a contact.
    
    Interactive prompts will guide you for any missing parameters.
    
    Examples:
        contact email add                              # Fully interactive
        contact email add "John"                       # Prompt for email
        contact email add "John" "john@example.com"   # Direct execution
    """
    # Validate email if provided
    if email is not None:
        email = validate_email(email)
    return _email_add_impl(contact_name, email)


@inject
@handle_service_errors
@auto_save
def _email_remove_impl(
    name: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Remove email address from a contact."""
    message = service.remove_email(name)
    console.print(f"[bold green]{message}[/bold green]")


@email_app.command(name="remove")
@progressive_params(
    contact_name=Container.contact_selector_factory
)
def email_remove_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
):
    """
    Remove email address from a contact.
    
    Supports progressive fulfillment:
        contact email remove                         # Interactive contact selection
        contact email remove "John"                  # Direct removal
    """
    return _email_remove_impl(contact_name)


# ============================================================================
# Address Management Commands
# ============================================================================

address_app = typer.Typer(
    help="Manage addresses for contacts",
    invoke_without_command=True
)


@inject
@handle_service_errors
@auto_save
def _address_set_impl(
    name: str,
    country: str,
    city: str,
    address_line: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Set address for a contact."""
    message = service.set_address(name, country, city, address_line)
    console.print(f"[bold green]{message}[/bold green]")


@address_app.command(name="set")
@progressive_params(
    contact_name=Container.contact_selector_factory,
    country=partial(Container.country_selector_factory, "Select country"),
    city=partial(Container.city_selector_factory, "Select city"),
    address_line=partial(Container.text_input_factory, "Enter street address", required=True)
)
def address_set_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
    country: Optional[str] = typer.Argument(None, help="Country code (e.g., UA, PL)"),
    city: Optional[str] = typer.Argument(None, help="City name"),
    address_line: Optional[str] = typer.Argument(None, help="Street address"),
):
    """
    Set address for a contact with interactive step-by-step selection.
    
    Interactive prompts will guide you for any missing parameters.
    The selection process: country -> city -> street address.
    
    Examples:
        contact address set                              # Fully interactive
        contact address set "John"                       # Prompt for country, city, address
        contact address set "John" "UA"                  # Prompt for city and address
        contact address set "John" "UA" "Kyiv"          # Prompt for address only
        contact address set "John" "UA" "Kyiv" "Main St. 1"  # Direct execution
    """
    return _address_set_impl(contact_name, country, city, address_line)


@inject
@handle_service_errors
@auto_save
def _address_remove_impl(
    name: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Remove address from a contact."""
    message = service.remove_address(name)
    console.print(f"[bold green]{message}[/bold green]")


@address_app.command(name="remove")
@progressive_params(
    contact_name=Container.contact_selector_factory
)
def address_remove_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
):
    """
    Remove address from a contact.
    
    Supports progressive fulfillment:
        contact address remove                         # Interactive contact selection
        contact address remove "John"                  # Direct removal
    """
    return _address_remove_impl(contact_name)


# ============================================================================
# Nested App Callbacks
# ============================================================================

@phone_app.callback(invoke_without_command=True)
def phone_callback(ctx: typer.Context):
    """Callback for phone command group. Shows menu if no subcommand."""
    if ctx.invoked_subcommand is None:
        return _phone_menu()


@birthday_app.callback(invoke_without_command=True)
def birthday_callback(ctx: typer.Context):
    """Callback for birthday command group. Shows menu if no subcommand."""
    if ctx.invoked_subcommand is None:
        return _birthday_menu()


@tag_app.callback(invoke_without_command=True)
def tag_callback(ctx: typer.Context):
    """Callback for tag command group. Shows menu if no subcommand."""
    if ctx.invoked_subcommand is None:
        return _tag_menu()


@email_app.callback(invoke_without_command=True)
def email_callback(ctx: typer.Context):
    """Callback for email command group. Shows menu if no subcommand."""
    if ctx.invoked_subcommand is None:
        return _email_menu()


@address_app.callback(invoke_without_command=True)
def address_callback(ctx: typer.Context):
    """Callback for address command group. Shows menu if no subcommand."""
    if ctx.invoked_subcommand is None:
        return _address_menu()


# ============================================================================
# Register Sub-Apps
# ============================================================================

app.add_typer(phone_app, name="phone")
app.add_typer(birthday_app, name="birthday")
app.add_typer(tag_app, name="tag")
app.add_typer(email_app, name="email")
app.add_typer(address_app, name="address")


# ============================================================================
# Interactive Menu
# ============================================================================

def _contact_menu():
    """
    Interactive contact management menu using generic auto_menu framework.
    
    The menu is generated automatically and calls commands with None parameters.
    Progressive params handles all the interactive prompting.
    """
    # Define main menu commands
    main_commands = menu_command_map(
        ("add", add_contact_command, "Add contact", (None, None)),
        ("edit", edit_contact_command, "Edit contact name", (None, None)),
        ("remove", remove_contact_command, "Remove contact", (None,)),
        ("show", show_contact_command, "Show contact details", (None,)),
        ("list", list_contacts_command, "List all contacts", (None, None)),
        ("phone", _phone_menu, "Manage phone numbers", ()),
        ("birthday", _birthday_menu, "Manage birthdays", ()),
        ("tag", _tag_menu, "Manage tags", ()),
        ("email", _email_menu, "Manage email addresses", ()),
        ("address", _address_menu, "Manage addresses", ()),
    )
    
    # Use generic auto_menu
    auto_menu(None, title="Contact Management Menu", commands=main_commands)


def _phone_menu():
    """Sub-menu for phone management."""
    phone_commands = menu_command_map(
        ("add", phone_add_command, "Add phone", (None, None)),
        ("edit", phone_edit_command, "Edit phone", (None, None, None)),
        ("change", phone_change_command, "Change phone", (None, None, None)),
        ("remove", phone_remove_command, "Remove phone", (None, None)),
        ("list", phone_list_command, "List phones", (None,)),
    )
    auto_menu(None, title="Phone Management", commands=phone_commands)


def _birthday_menu():
    """Sub-menu for birthday management."""
    birthday_commands = menu_command_map(
        ("add", birthday_add_command, "Add birthday", (None, None)),
        ("edit", birthday_edit_command, "Edit birthday", (None, None)),
        ("show", birthday_show_command, "Show birthday", (None,)),
        ("upcoming", birthday_upcoming_command, "Show upcoming birthdays", ()),
    )
    auto_menu(None, title="Birthday Management", commands=birthday_commands)


def _tag_menu():
    """Sub-menu for tag management."""
    tag_commands = menu_command_map(
        ("add", tag_add_command, "Add tags", (None, None)),
        ("remove", tag_remove_command, "Remove tag", (None, None)),
        ("clear", tag_clear_command, "Clear all tags", (None,)),
        ("list", tag_list_command, "List tags", (None,)),
    )
    auto_menu(None, title="Tag Management", commands=tag_commands)


def _email_menu():
    """Sub-menu for email management."""
    email_commands = menu_command_map(
        ("add", email_add_command, "Add email", (None, None)),
        ("remove", email_remove_command, "Remove email", (None,)),
    )
    auto_menu(None, title="Email Management", commands=email_commands)


def _address_menu():
    """Sub-menu for address management."""
    address_commands = menu_command_map(
        ("set", address_set_command, "Set address", (None, None, None, None)),
        ("remove", address_remove_command, "Remove address", (None,)),
    )
    auto_menu(None, title="Address Management", commands=address_commands)


@app.callback(invoke_without_command=True)
def contact_callback(ctx: typer.Context):
    """
    Callback for contact command group.
    
    If no subcommand is provided, launches the interactive menu.
    """
    if ctx.invoked_subcommand is None:
        return _contact_menu()

