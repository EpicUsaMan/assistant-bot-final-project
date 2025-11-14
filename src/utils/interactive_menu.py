"""
Interactive menu framework for command groups.

Provides decorators and utilities to automatically generate interactive menus
for command groups without hard-coding menu logic.

Usage:
    @app.callback(invoke_without_command=True)
    def notes_callback(ctx: typer.Context):
        if ctx.invoked_subcommand is None:
            return auto_menu(ctx, title="Notes Management Menu")
"""

from typing import Dict, Callable, Optional, Any
import typer
import questionary
from rich.console import Console

console = Console()


class MenuRegistry:
    """
    Registry for command group menus.
    
    Stores metadata about commands that can be shown in interactive menus.
    """
    
    def __init__(self):
        """Initialize empty registry."""
        self._command_groups: Dict[str, Dict[str, Any]] = {}
    
    def register_command_group(
        self,
        group_name: str,
        commands: Dict[str, tuple[Callable, str]]
    ):
        """
        Register a command group with its available commands.
        
        Args:
            group_name: Name of the command group (e.g., "notes", "search")
            commands: Dict of {command_key: (command_func, display_name)}
        """
        self._command_groups[group_name] = commands
    
    def get_command_group(self, group_name: str) -> Optional[Dict[str, tuple[Callable, str]]]:
        """
        Get commands for a group.
        
        Args:
            group_name: Name of the command group
            
        Returns:
            Dict of commands or None
        """
        return self._command_groups.get(group_name)
    
    def has_group(self, group_name: str) -> bool:
        """Check if group is registered."""
        return group_name in self._command_groups


# Global registry
_menu_registry = MenuRegistry()


def get_menu_registry() -> MenuRegistry:
    """Get the global menu registry."""
    return _menu_registry


def register_menu(
    group_name: str,
    commands: Dict[str, tuple[Callable, str]]
) -> Callable:
    """
    Decorator to register commands for a menu.
    
    Args:
        group_name: Name of the command group
        commands: Dict of {command_key: (command_func, display_name)}
        
    Returns:
        Decorator function
        
    Example:
        @register_menu("notes", {
            "add": (add_note_command, "Add note"),
            "list": (list_notes_command, "List notes"),
            "edit": (edit_note_command, "Edit note"),
        })
        def notes_callback(ctx: typer.Context):
            if ctx.invoked_subcommand is None:
                return auto_menu(ctx, "notes")
    """
    def decorator(func: Callable) -> Callable:
        _menu_registry.register_command_group(group_name, commands)
        return func
    return decorator


def auto_menu(
    ctx: typer.Context,
    group_name: Optional[str] = None,
    title: Optional[str] = None,
    commands: Optional[Dict[str, tuple[Callable, str, Optional[tuple]]]] = None
) -> None:
    """
    Automatically generate and run an interactive menu.
    
    The menu discovers commands automatically from the registry or uses
    provided commands. It calls commands with None parameters, letting
    @progressive_params handle the interactive prompting.
    
    Args:
        ctx: Typer context
        group_name: Name of the command group to load from registry
        title: Menu title to display
        commands: Optional dict of {key: (func, display_name, args_tuple)}
                 If provided, overrides registry lookup
        
    Example:
        # Automatic from registry
        auto_menu(ctx, "notes", "Notes Management")
        
        # Manual command list
        auto_menu(ctx, title="Notes Menu", commands={
            "add": (add_note_command, "Add note", (None, None, None)),
            "list": (list_notes_command, "List notes", (None,))
        })
    """
    # Get commands from registry if not provided
    if commands is None and group_name:
        commands = _menu_registry.get_command_group(group_name)
        if commands is None:
            console.print(f"[red]Error: No commands registered for '{group_name}'[/red]")
            return
    
    if not commands:
        console.print("[red]Error: No commands available for menu[/red]")
        return
    
    # Default title
    if title is None:
        title = f"{group_name.title()} Menu" if group_name else "Interactive Menu"
    
    while True:
        console.print(f"\n[bold cyan]{title}[/bold cyan]\n")
        
        # Build menu choices
        choices = [display_name for _, (_, display_name, *_) in sorted(commands.items())]
        choices.append("Exit")
        
        action = questionary.select(
            "What would you like to do?",
            choices=choices,
            style=questionary.Style([
                ('selected', 'fg:cyan bold'),
                ('pointer', 'fg:cyan bold'),
            ])
        ).ask()
        
        if action == "Exit" or action is None:
            console.print(f"[yellow]Exiting {group_name or 'menu'}.[/yellow]")
            break
        
        # Find and call the command function
        for cmd_key, cmd_data in commands.items():
            func, display_name = cmd_data[0], cmd_data[1]
            args = cmd_data[2] if len(cmd_data) > 2 else ()
            
            if display_name == action:
                # Call command with None parameters
                if args:
                    func(*args)
                else:
                    func()
                break


def menu_command_map(
    *command_configs: tuple[str, Callable, str, tuple]
) -> Dict[str, tuple[Callable, str, tuple]]:
    """
    Helper to build command map for auto_menu.
    
    Args:
        *command_configs: Tuples of (key, func, display_name, args_tuple)
        
    Returns:
        Dict suitable for auto_menu
        
    Example:
        commands = menu_command_map(
            ("add", add_note_command, "Add note", (None, None, None)),
            ("list", list_notes_command, "List notes", (None,)),
            ("edit", edit_note_command, "Edit note", (None, None, None))
        )
        auto_menu(ctx, title="Notes", commands=commands)
    """
    return {
        key: (func, display, args)
        for key, func, display, args in command_configs
    }

