"""
Autocomplete helpers for Typer commands.

Provides shell completion callbacks for contact names, note names, and tags.
These functions are used by both shell autocomplete (Typer) and
REPL autocomplete (prompt_toolkit).

Uses dependency injection pattern with _impl functions following MVCS architecture.
"""

from typing import List, Optional
from dependency_injector.wiring import Provide, inject
from src.container import Container
from src.services.note_service import NoteService
from src.models.group import DEFAULT_GROUP_ID


@inject
def _complete_contact_name_impl(
    incomplete: str = "",
    service: NoteService = Provide[Container.note_service]
) -> List[str]:
    """
    Implementation: Get contact names for autocomplete using DI.
    
    Args:
        incomplete: The partial string typed by the user
        service: Note service (injected via DI)
        
    Returns:
        List of matching contact names
    """
    try:
        # Check if contacts exist
        if not service.has_contacts():
            return []
        
        # Get all contact names from service
        contacts = service.list_contacts()
        # Extract contact name from "group:name" format
        names = [name.split(":", 1)[1] if ":" in name else name for name, _ in contacts]
        
        # Filter by incomplete string (case-insensitive)
        if incomplete:
            incomplete_lower = incomplete.lower()
            names = [name for name in names if name.lower().startswith(incomplete_lower)]
        
        return sorted(names)
    except Exception:
        return []


def complete_contact_name(ctx=None, args=None, incomplete: str = "") -> List[str]:
    """
    Shell completion callback for contact names.
    
    Compatible with both Typer (ctx, args, incomplete) and simple (incomplete) signatures.
    Returns list of contact names that match the incomplete string.
    Used for TAB completion in shell.
    
    Args:
        ctx: Click context (optional, for Typer compatibility)
        args: Click parameter args (optional, for Typer compatibility)
        incomplete: The partial string typed by the user
        
    Returns:
        List of matching contact names
    """
    return _complete_contact_name_impl(incomplete)


@inject
def _complete_note_name_impl(
    incomplete: str = "",
    contact_name: Optional[str] = None,
    service: NoteService = Provide[Container.note_service]
) -> List[str]:
    """
    Implementation: Get note names for autocomplete using DI.
    
    Can work in two modes:
    1. With contact_name: Returns notes for specific contact (context-aware)
    2. Without contact_name: Returns ALL notes from ALL contacts (fallback)
    
    Args:
        incomplete: The partial string typed by the user
        contact_name: Contact name from context (optional)
        service: Note service (injected via DI)
        
    Returns:
        List of matching note names
    """
    try:
        # Get note names based on mode
        if contact_name:
            # Context-aware: Get notes for specific contact only
            try:
                notes = service.list_notes(contact_name)
                note_names = sorted([note.name for note in notes])
            except ValueError:
                note_names = []
        else:
            # Fallback: Get all note names from all contacts
            all_note_names = set()
            contacts = service.list_contacts()
            for key, _ in contacts:
                # Extract contact name from "group:name" format
                contact_name_only = key.split(":", 1)[1] if ":" in key else key
                try:
                    notes = service.list_notes(contact_name_only)
                    all_note_names.update(note.name for note in notes)
                except ValueError:
                    pass
            note_names = sorted(all_note_names)
        
        # Filter by incomplete string (case-insensitive)
        if incomplete:
            incomplete_lower = incomplete.lower()
            note_names = [name for name in note_names if name.lower().startswith(incomplete_lower)]
        
        return note_names
    except Exception:
        return []


def complete_note_name(ctx=None, args=None, incomplete: str = "") -> List[str]:
    """
    Shell completion callback for note names.
    
    Compatible with both Typer (ctx, args, incomplete) and REPL (incomplete, contact_name) signatures.
    Can work in two modes:
    1. With contact_name from ctx: Returns notes for specific contact (context-aware)
    2. Without contact_name: Returns ALL notes from ALL contacts (fallback)
    
    Args:
        ctx: Click context (optional, for Typer compatibility)
        args: Click parameter args (optional, for Typer compatibility)
        incomplete: The partial string typed by the user
        
    Returns:
        List of matching note names
    """
    # Try to get contact_name from context (for context-aware completion)
    contact_name = None
    if ctx and hasattr(ctx, 'params'):
        contact_name = ctx.params.get('contact_name')
    
    return _complete_note_name_impl(incomplete, contact_name)


@inject
def _complete_tag_impl(
    incomplete: str = "",
    contact_name: Optional[str] = None,
    note_name: Optional[str] = None,
    service: NoteService = Provide[Container.note_service]
) -> List[str]:
    """
    Implementation: Get tag names for autocomplete using DI.
    
    Can work in three modes:
    1. With contact_name and note_name: Returns tags for specific note (context-aware)
    2. With contact_name only: Returns all tags from all notes of that contact
    3. Without context: Returns ALL tags from ALL notes in ALL contacts (fallback)
    
    Args:
        incomplete: The partial string typed by the user
        contact_name: Contact name from context (optional)
        note_name: Note name from context (optional)
        service: Note service (injected via DI)
        
    Returns:
        List of matching tag names
    """
    try:
        # Get tag names based on mode
        all_tags = set()
        
        if contact_name and note_name:
            # Context-aware: Get tags for specific note only
            try:
                tags_list = service.note_list_tags(contact_name, note_name)
                all_tags.update(tags_list)
            except ValueError:
                pass
        elif contact_name:
            # Semi-context-aware: Get all tags from all notes of specific contact
            try:
                notes = service.list_notes(contact_name)
                for note in notes:
                    all_tags.update(note.tags.value)  # Fixed: use .value to get list
            except ValueError:
                pass
        else:
            # Fallback: Get all tags from all notes in all contacts
            contacts = service.list_contacts()
            for key, _ in contacts:
                # Extract contact name from "group:name" format
                contact_name_only = key.split(":", 1)[1] if ":" in key else key
                try:
                    notes = service.list_notes(contact_name_only)
                    for note in notes:
                        all_tags.update(note.tags.value)  # Fixed: use .value to get list
                except ValueError:
                    pass
        
        # Convert to sorted list
        tag_names = sorted(all_tags)
        
        # Filter by incomplete string (case-insensitive)
        if incomplete:
            incomplete_lower = incomplete.lower()
            tag_names = [tag for tag in tag_names if tag.lower().startswith(incomplete_lower)]
        
        return tag_names
    except Exception:
        return []


def complete_tag(ctx=None, args=None, incomplete: str = "") -> List[str]:
    """
    Shell completion callback for tag names.
    
    Compatible with both Typer (ctx, args, incomplete) and REPL (incomplete, contact_name, note_name) signatures.
    Can work in three modes:
    1. With contact_name and note_name from ctx: Returns tags for specific note (context-aware)
    2. With contact_name only: Returns all tags from all notes of that contact
    3. Without context: Returns ALL tags from ALL notes in ALL contacts (fallback)
    
    Args:
        ctx: Click context (optional, for Typer compatibility)
        args: Click parameter args (optional, for Typer compatibility)
        incomplete: The partial string typed by the user
        
    Returns:
        List of matching tag names
    """
    # Try to get contact_name and note_name from context (for context-aware completion)
    contact_name = None
    note_name = None
    if ctx and hasattr(ctx, 'params'):
        contact_name = ctx.params.get('contact_name')
        note_name = ctx.params.get('note_name')
    
    return _complete_tag_impl(incomplete, contact_name, note_name)

