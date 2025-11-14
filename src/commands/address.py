"""
Unified address commands with subcommands.

All address-related operations organized under 'address' command:
- address set
- address remove
"""

import typer
from typing import Optional
from functools import partial
from dependency_injector.wiring import Provide, inject
from rich.console import Console

from src.container import Container
from src.services.contact_service import ContactService
from src.utils.command_decorators import handle_service_errors, auto_save
from src.utils.autocomplete import complete_contact_name
from src.utils.progressive_params import progressive_params
from src.utils.interactive_menu import auto_menu, menu_command_map

app = typer.Typer(
    help="Manage addresses for contacts",
    invoke_without_command=True
)
console = Console()


# ============================================================================
# Set Address Command
# ============================================================================

@inject
@handle_service_errors
@auto_save
def _set_address_impl(
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


@app.command(name="set")
@progressive_params(
    contact_name=Container.contact_selector_factory,
    country=partial(Container.country_selector_factory, "Select country:"),
    city=partial(Container.city_selector_factory, "Select city:"),
    address_line=partial(Container.text_input_factory, "Enter street address:", required=True)
)
def set_address_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
    country: Optional[str] = typer.Argument(None, help="Country code (e.g., UA, PL)"),
    city: Optional[str] = typer.Argument(None, help="City name"),
    address_line: Optional[str] = typer.Argument(None, help="Street address"),
):
    """
    Set address for a contact with interactive step-by-step selection.
    
    Interactive prompts will guide you for any missing parameters.
    The selection process: country → city → street address.
    
    Examples:
        address set                              # Fully interactive
        address set "John"                       # Prompt for country, city, address
        address set "John" "UA"                  # Prompt for city and address
        address set "John" "UA" "Kyiv"          # Prompt for address only
        address set "John" "UA" "Kyiv" "Main St. 1"  # Direct execution
    """
    return _set_address_impl(contact_name, country, city, address_line)


# ============================================================================
# Remove Address Command
# ============================================================================

@inject
@handle_service_errors
@auto_save
def _remove_address_impl(
    name: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation: Remove address from a contact."""
    message = service.remove_address(name)
    console.print(f"[bold green]{message}[/bold green]")


@app.command(name="remove")
@progressive_params(
    contact_name=Container.contact_selector_factory
)
def remove_address_command(
    contact_name: Optional[str] = typer.Argument(None, help="Contact name", autocompletion=complete_contact_name),
):
    """
    Remove address from a contact.
    
    Supports progressive fulfillment:
        address remove                         # Interactive contact selection
        address remove "John"                  # Direct removal
    """
    return _remove_address_impl(contact_name)


# ============================================================================
# Interactive Menu
# ============================================================================

def _address_menu():
    """
    Interactive address management menu using generic auto_menu framework.
    
    The menu is generated automatically and calls commands with None parameters.
    Progressive params handles all the interactive prompting.
    """
    # Define address menu commands
    address_commands = menu_command_map(
        ("set", set_address_command, "Set address", (None, None, None, None)),
        ("remove", remove_address_command, "Remove address", (None,)),
    )
    
    # Use generic auto_menu
    auto_menu(None, title="Address Management", commands=address_commands)


@app.callback(invoke_without_command=True)
def address_callback(ctx: typer.Context):
    """
    Callback for address command group.
    
    If no subcommand is provided, launches the interactive menu.
    """
    if ctx.invoked_subcommand is None:
        return _address_menu()

