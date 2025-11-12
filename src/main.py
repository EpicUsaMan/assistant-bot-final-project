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
from rich.console import Console
from rich.panel import Panel
from src.container import Container

app = typer.Typer(
    name="assistant-bot",
    help="Console bot assistant for managing contacts with names, phone numbers, and birthdays.",
    add_completion=False,
)
console = Console()

container = Container()
container.config.storage.filename.from_value("addressbook.pkl")

# Track if container is already wired and commands registered
_container_wired = False
_commands_registered = False


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
            container.wire(modules=module_names)
            _container_wired = True
        except Exception as e:
            # If wiring fails, commands can still work by calling inner functions directly
            console.print(f"[yellow]Warning: Failed to wire container: {e}[/yellow]")
    
    # Step 3: Mount all command apps to the main app
    for module in module_objects:
        try:
            app.add_typer(module.app, name="")
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to mount command app: {e}[/yellow]")
    
    _commands_registered = True

from rich import print
from rich.tree import Tree

def show_menu() -> Tree:
    
    tree = Tree("[bold green]Welcome to the Assistant Bot![/bold green]\n\n[bold cyan]Available commands[/]")
    general = tree.add("🤖 [yellow]General[/]")
    contacts = tree.add("📇 [yellow]Contacts[/]")
    birthdays = tree.add("🎂 [yellow]Birthdays[/]")

    general.add("[bold cyan]hello[/] — Get a greeting")
    general.add("[bold cyan]exit[/] or [bold cyan]quit[/] — Exit the program")

    contacts.add("[bold cyan]add[/] — Add a contact")
    contacts.add("[bold cyan]change[/] — Change phone number")
    contacts.add("[bold cyan]phone[/] — Show phone numbers")
    contacts.add("[bold cyan]all[/] — Show all contacts")

    birthdays.add("[bold cyan]add-birthday [DD.MM.YYYY][/] — Add birthday")
    birthdays.add("[bold cyan]show-birthday[/] — Show birthday")
    birthdays.add("[bold cyan]birthdays[/] — Show upcoming birthdays")

    return tree

@app.command()
def interactive():
    """
    Start interactive REPL mode.
    """
    from click_repl import repl
    from click import Context
    
    console.print(show_menu())
    ctx = Context(typer.main.get_command(app))
    
    try:
        repl(ctx)
    except (EOFError, KeyboardInterrupt):
        console.print("\n[bold green]Good bye![/bold green]")

def run_interactive():
    """
    Launch the interactive REPL mode directly.
    
    This function can be called programmatically to start interactive mode.
    Commands are registered and wired by auto_register_commands().
    """
    
    auto_register_commands()
    console.print(show_menu())
    
    try:
        from click_repl import repl
        from click import Context
        ctx = Context(typer.main.get_command(app))
        repl(ctx)
    except (EOFError, KeyboardInterrupt):
        console.print("\n[bold green]Good bye![/bold green]")


def main():
    """
    Main entry point for the CLI application.
    
    Auto-registers commands (which also wires the DI container) and launches
    the Typer app. If no arguments are provided, automatically starts interactive mode.
    """
    auto_register_commands()
    
    # If no arguments provided, launch interactive mode by default
    if len(sys.argv) == 1:
        run_interactive()
    else:
        app()


if __name__ == "__main__":
    main()





