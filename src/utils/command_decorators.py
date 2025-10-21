"""
Command decorators for standardized error handling and auto-save.

These decorators provide:
1. Consistent error handling across all commands
2. Automatic data persistence after UPDATE operations
3. Clear separation between READ and UPDATE commands

Usage:
    READ commands (only error handling):
        @inject
        @handle_service_errors
        def _phone_impl(...):
            ...
    
    UPDATE commands (error handling + auto-save):
        @inject
        @handle_service_errors
        @auto_save
        def _add_impl(...):
            ...
"""

import inspect
import sys
from functools import wraps
from typing import Callable, Any

import typer
from rich.console import Console

console = Console()


def _is_interactive_mode() -> bool:
    """
    Check if running in interactive REPL mode.
    
    Returns:
        True if in REPL mode, False otherwise
    """
    return 'click_repl' in sys.modules


def handle_service_errors(func: Callable) -> Callable:
    """
    Handle errors from service layer (business logic, not format validation).
    
    Format validation errors are caught by Typer callbacks at parameter level.
    This decorator catches:
    - ValueError: Business logic errors from services/models
    - KeyError: Record not found errors
    
    In interactive REPL mode, errors are displayed but don't exit the session.
    In CLI mode, errors cause the program to exit with code 1.
    
    When adding new service dependencies with custom exceptions:
    1. Import the exception class
    2. Add it to the except clauses below
    3. Provide user-friendly error message
    
    Example:
        # If using email_validator library:
        from email_validator import EmailNotValidError
        
        except EmailNotValidError as e:
            console.print(f"[bold red]Invalid email:[/bold red] {str(e)}")
            if not _is_interactive_mode():
                raise typer.Exit(1)
            return None
    
    Args:
        func: The command implementation function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            if not _is_interactive_mode():
                raise typer.Exit(1)
            return None
        except KeyError as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            if not _is_interactive_mode():
                raise typer.Exit(1)
            return None
    return wrapper


def auto_save(func: Callable) -> Callable:
    """
    Automatically save address book after successful UPDATE operations.
    
    Use this decorator on commands that modify data:
    - add (add contact or phone)
    - change (edit phone number)
    - add_birthday (add birthday to contact)
    - delete (future command)
    
    DO NOT use on READ commands:
    - phone (show phones)
    - show_birthday (show birthday)
    - all (show all contacts)
    - birthdays (show upcoming birthdays)
    
    The decorated function must have these parameters in its signature:
    - service: ContactService instance
    - filename: str (storage filename)
    
    Args:
        func: The command implementation function to wrap
        
    Returns:
        Wrapped function that auto-saves after successful execution
        
    Example:
        @inject
        @handle_service_errors
        @auto_save
        def _add_impl(
            name: str,
            phone: str,
            service: ContactService = Provide[Container.contact_service],
            filename: str = Provide[Container.config.storage.filename],
        ):
            message = service.add_contact(name, phone)
            console.print(f"[bold green]{message}[/bold green]")
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)
        
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        
        service = bound.arguments.get('service')
        filename = bound.arguments.get('filename')
        
        if service and filename:
            service.address_book.save_to_file(filename)
        
        return result
    return wrapper

