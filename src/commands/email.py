"""
Unified email commands with subcommands.

All email-related operations organized under 'email' command:
- email add
- email remove
"""

import typer
from typing import Optional
from functools import partial
from dependency_injector.wiring import Provide, inject
from rich.console import Console

from src.container import Container
from src.services.contact_service import ContactService
from src.utils.command_decorators import handle_service_errors, auto_save
from src.utils.validators import validate_email
from src.utils.autocomplete import complete_contact_name
from src.utils.progressive_params import progressive_params
from src.utils.interactive_menu import auto_menu, menu_command_map

app = typer.Typer(
    help="Manage email addresses for contacts",
    invoke_without_command=True
)
console = Console()


# ============================================================================
# Add Email Command
# ============================================================================

@inject
@handle_service_errors
@auto_save
def _add_email_impl(
    name: str,
    email: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Add or update email address for a contact."""
    message = service.add_email(name, email)
    console.print(f"[bold green]{message}[/bold green]")


@app.command(name="add")
@progressive_params(
    contact_name=Container.contact_selector_factory,
    email=partial(Container.email_input_factory, "Enter email address:", required=True)
)
def add_email_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
    email: Optional[str] = typer.Argument(None, help="Email address"),
):
    """
    Add or update email address for a contact.
    
    Interactive prompts will guide you for any missing parameters.
    
    Examples:
        email add                              # Fully interactive
        email add "John"                       # Prompt for email
        email add "John" "john@example.com"   # Direct execution
    """
    # Validate email if provided
    if email is not None:
        email = validate_email(email)
    return _add_email_impl(contact_name, email)


# ============================================================================
# Remove Email Command
# ============================================================================

@inject
@handle_service_errors
@auto_save
def _remove_email_impl(
    name: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Remove email address from a contact."""
    message = service.remove_email(name)
    console.print(f"[bold green]{message}[/bold green]")


@app.command(name="remove")
@progressive_params(
    contact_name=Container.contact_selector_factory
)
def remove_email_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
):
    """
    Remove email address from a contact.
    
    Supports progressive fulfillment:
        email remove                         # Interactive contact selection
        email remove "John"                  # Direct removal
    """
    return _remove_email_impl(contact_name)


# ============================================================================
# Interactive Menu
# ============================================================================

def _email_menu():
    """
    Interactive email management menu using generic auto_menu framework.
    
    The menu is generated automatically and calls commands with None parameters.
    Progressive params handles all the interactive prompting.
    """
    # Define email menu commands
    email_commands = menu_command_map(
        ("add", add_email_command, "Add or update email", (None, None)),
        ("remove", remove_email_command, "Remove email", (None,)),
    )
    
    # Use generic auto_menu
    auto_menu(None, title="Email Management", commands=email_commands)


@app.callback(invoke_without_command=True)
def email_callback(ctx: typer.Context):
    """
    Callback for email command group.
    
    If no subcommand is provided, launches the interactive menu.
    """
    if ctx.invoked_subcommand is None:
        return _email_menu()

