"""
Quit command for gracefully exiting the application.

This command is an alias for the exit command, providing an alternative
way for users to exit the CLI application.
"""

import typer
from rich.console import Console

app = typer.Typer(help="Quit the application")
console = Console()


@app.command(name="quit")
def quit_command():
    """
    Quit the application gracefully.
    
    This is an alias for the exit command.
    Raises EOFError to properly exit interactive REPL mode.
    The goodbye message is handled by the REPL handler in main.py.
    """
    raise EOFError

