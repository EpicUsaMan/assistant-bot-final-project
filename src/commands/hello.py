"""
Hello command - Get a greeting from the bot.

Simple command that doesn't require any services.
"""

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command(name="hello")
def hello_command():
    """
    Get a greeting from the bot.
    """
    console.print("[bold green]How can I help you?[/bold green]")





