"""
Exit command for gracefully exiting the application.

This command provides a user-friendly way to exit the CLI application.
"""

import typer
from rich.console import Console

app = typer.Typer(help="Exit the application")
console = Console()


@app.command(name="exit")
def exit_command():
    """
    Exit the application gracefully.
    
    Raises EOFError to properly exit interactive REPL mode.
    The goodbye message is handled by the REPL handler in main.py.
    """
    raise EOFError

