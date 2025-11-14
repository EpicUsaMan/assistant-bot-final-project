"""
Main CLI application entry point with auto-registration and dependency injection.

This module implements the main Typer application that automatically discovers
and registers all commands from the src/commands/ directory. It also provides
interactive REPL mode for backward compatibility.
"""

import importlib
import pkgutil
import sys
from pathlib import Path

# Add project root to Python path to allow 'src' imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import typer
import click
from rich.console import Console
from rich.panel import Panel
from src.container import Container
from src.services.contact_service import ContactService

app = typer.Typer(
    name="assistant-bot",
    help="Console bot assistant for managing contacts with names, phone numbers, and birthdays.",
    add_completion=True,
)
console = Console()

container = Container()
container.config.storage.filename.from_value("addressbook.pkl")

# Track if container is already wired and commands registered
_container_wired = False
_commands_registered = False

def _make_group_prompt() -> str:
    """Return dynamic prompt with current group id."""
    service: ContactService = container.contact_service()
    group_id = service.get_current_group()
    return f"[{group_id}] > "


def _iter_commands() -> list[tuple[str, str]]:
    """Collect (name, help) for top-level commands, skipping internal ones."""
    root_cmd: click.Command = typer.main.get_command(app)
    result: list[tuple[str, str]] = []

    for name, cmd in root_cmd.commands.items():
        # filter tech commands if needed
        if name in {"interactive"}:
            continue
        help_line = (cmd.help or "").strip().splitlines()[0] if cmd.help else ""
        result.append((name, help_line))

    # sorted by name
    result.sort(key=lambda x: x[0])
    return result


def _build_welcome_text() -> str:
    lines: list[str] = [
        "[bold green]Welcome to the Assistant Bot![/bold green]\n",
        "Available commands:",
    ]
    for name, help_line in _iter_commands():
        if help_line:
            lines.append(f"  • [cyan]{name}[/cyan] - {help_line}")
        else:
            lines.append(f"  • [cyan]{name}[/cyan]")
    lines.append(
        "\nType [cyan]--help[/cyan] after any command to see details, "
        "e.g. [cyan]add --help[/cyan]."
    )
    return "\n".join(lines)


def _print_welcome_panel() -> None:
    console.print(
        Panel(
            _build_welcome_text(),
            title="[bold]Assistant Bot[/bold]",
            border_style="green",
        )
    )

def auto_register_commands():
    """
    Automatically discover, import, wire, and register all commands from src/commands/ directory.
    
    Uses a two-level function pattern where:
    - Outer function (visible to Typer) has only CLI parameters
    - Inner function (with @inject) has CLI + injected parameters
    
    This allows dependency injection to work while keeping Typer happy.
    """
    global _commands_registered, _container_wired
    
    if _commands_registered:
        return  # Already registered
    
    commands_path = Path(__file__).parent / "commands"
    module_objects = []
    module_names = []
    
    # Step 1: Import all command modules
    for module_info in pkgutil.iter_modules([str(commands_path)]):
        module_name = module_info.name
        
        if module_name.startswith("_"):
            continue
        
        try:
            module = importlib.import_module(f"src.commands.{module_name}")
            if hasattr(module, "app"):
                module_objects.append(module)
                module_names.append(f"src.commands.{module_name}")
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to import command '{module_name}': {e}[/yellow]")
    
    # Step 2: Wire the container for dependency injection
    # With the two-level function pattern, we only need to wire the modules
    # so that the inner @inject functions can access the container
    if not _container_wired and module_names:
        try:
            # Wire command modules + utility modules that use DI
            all_modules = module_names + [
                "src.utils.autocomplete",  # Autocomplete uses @inject for service resolution
                "src.utils.progressive_params",  # Progressive params uses lazy service resolution
            ]
            container.wire(modules=all_modules)
            _container_wired = True
        except Exception as e:
            # If wiring fails, commands can still work by calling inner functions directly
            console.print(f"[yellow]Warning: Failed to wire container: {e}[/yellow]")
    
    # Step 3: Mount all command apps to the main app
    for idx, module in enumerate(module_objects):
        try:
            module_name = module_names[idx].split('.')[-1]  # Get the module name
            
            # Special handling for command groups (subcommands)
            if module_name == "notes":
                # Register as subcommand group: notes add, notes edit, etc.
                app.add_typer(module.app, name="notes")
            elif module_name == "search":
                # Register as subcommand group: search contacts, search notes, search menu
                app.add_typer(module.app, name="search")
            else:
                # Register commands at root level
                app.add_typer(module.app, name="")
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to mount command app: {e}[/yellow]")
    
    _commands_registered = True


@app.command()
def interactive():
    """
    Start interactive REPL mode.
    """
    from click_repl import repl
    from click import Context
    from src.utils.repl_completer import create_context_aware_completer_for_repl
    
    _print_welcome_panel()

    ctx = Context(typer.main.get_command(app))
    
    # Create context-aware completer that fixes parameter positioning
    custom_completer = create_context_aware_completer_for_repl(ctx)
    
    prompt_kwargs = {
        "message": _make_group_prompt,
        "completer": custom_completer
    }

    try:
        repl(ctx, prompt_kwargs=prompt_kwargs)
    except (EOFError, KeyboardInterrupt):
        console.print("\n[bold green]Good bye![/bold green]")


def run_interactive():
    """
    Launch the interactive REPL mode directly.
    
    This function can be called programmatically to start interactive mode.
    Commands are registered and wired by auto_register_commands().
    """
    auto_register_commands()
    from click_repl import repl
    from click import Context
    from src.utils.repl_completer import create_context_aware_completer_for_repl

    _print_welcome_panel()

    ctx = Context(typer.main.get_command(app))
    
    console.print(Panel(
        "[bold green]Welcome to the Assistant Bot![/bold green]\n\n"
        "Available commands:\n"
        "  • [cyan]hello[/cyan] - Get a greeting\n"
        "  • [cyan]add[/cyan] [name] [phone] - Add a contact\n"
        "  • [cyan]change[/cyan] [name] [old_phone] [new_phone] - Change phone number\n"
        "  • [cyan]delete[/cyan] [name] - Delete a contact\n"
        "  • [cyan]phone[/cyan] [name] - Show phone numbers\n"
        "  • [cyan]all[/cyan] - Show all contacts\n"
        "  • [cyan]add-birthday[/cyan] [name] [DD.MM.YYYY] - Add birthday\n"
        "  • [cyan]show-birthday[/cyan] [name] - Show birthday\n"
        "  • [cyan]birthdays[/cyan] - Show upcoming birthdays\n"
        "  • [cyan]exit[/cyan] or [cyan]quit[/cyan] - Exit the program\n",
        title="[bold]Assistant Bot[/bold]",
        border_style="green"
    ))
    # Create context-aware completer that fixes parameter positioning
    custom_completer = create_context_aware_completer_for_repl(ctx)
    
    prompt_kwargs = {
        "message": _make_group_prompt,
        "completer": custom_completer
    }

    try:
        repl(ctx, prompt_kwargs=prompt_kwargs)
    except (EOFError, KeyboardInterrupt):
        console.print("\n[bold green]Good bye![/bold green]")


def main():
    """
    Main entry point for the CLI application.
    
    Auto-registers commands (which also wires the DI container) and launches
    the Typer app. If no arguments are provided, automatically starts interactive mode.
    """
    auto_register_commands()
    
    if len(sys.argv) == 1:
        run_interactive()
    else:
        app()

if __name__ == "__main__":
    main()