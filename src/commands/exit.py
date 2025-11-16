"""
Exit command for gracefully exiting the application.

Note: 'quit' is handled as an alias in the REPL (transformed to 'exit' automatically).
"""

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


def _exit_impl():
    """
    Implementation: Exit the application gracefully.
    
    Raises EOFError to properly exit interactive REPL mode.
    The goodbye message is handled by the REPL handler in main.py.
    """
    raise EOFError


@app.command(name="exit")
def exit_command():
    """Exit the application gracefully"""
    return _exit_impl()

