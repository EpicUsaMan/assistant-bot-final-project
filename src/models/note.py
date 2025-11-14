"""Note model for storing text notes with tags."""

from typing import Optional
from src.models.field import Field
from src.models.tags import Tags
from src.utils.validators import is_valid_tag, normalize_tag


class Note(Field):
    """
    Class for storing a text note with name (as ID), content, and tags.
    
    Attributes:
        name: Note name/title (acts as unique identifier)
        content: Note text content
        tags: Note tags (Tags object)
    """
    
    def __init__(self, name: str, content: str = "") -> None:
        """
        Initialize a note with name and optional content.
        
        Args:
            name: The note's name/title (required, acts as ID)
            content: The note's text content (default: empty string)
            
        Raises:
            ValueError: If name is empty
        """
        if not name or not name.strip():
            raise ValueError("Note name cannot be empty")
        
        super().__init__(name.strip())
        self.name = self.value
        self.content = content
        self.tags = Tags()
    
    def update_content(self, content: str) -> None:
        """
        Update the note's content.
        
        Args:
            content: New text content for the note
        """
        self.content = content
    
    def add_tag(self, tag: str) -> None:
        """
        Add a single tag to the note.
        
        Args:
            tag: Tag to add
            
        Raises:
            ValueError: If tag format is invalid
        """
        normalized = normalize_tag(tag)
        if not is_valid_tag(normalized):
            raise ValueError(f"Invalid tag: '{tag}'")
        self.tags.add(normalized)
    
    def remove_tag(self, tag: str) -> None:
        """
        Remove a single tag from the note.
        
        Args:
            tag: Tag to remove
        """
        normalized = normalize_tag(tag)
        self.tags.remove(normalized)
    
    def clear_tags(self) -> None:
        """
        Clear all tags from the note.
        """
        self.tags.clear()
    
    def tags_list(self) -> list[str]:
        """
        Get list of all tags.
        
        Returns:
            List of tag strings
        """
        return self.tags.as_list()
    
    def has_tags_all(self, tags: list[str]) -> bool:
        """
        Return True if note has all of the specified tags (AND).
        
        Args:
            tags: List of tags to check
            
        Returns:
            True if note has all tags, False otherwise
        """
        return all(tag in self.tags.as_list() for tag in tags)
    
    def has_tags_any(self, tags: list[str]) -> bool:
        """
        Return True if note has any of the specified tags (OR).
        
        Args:
            tags: List of tags to check
            
        Returns:
            True if note has at least one tag, False otherwise
        """
        return any(tag in self.tags.as_list() for tag in tags)
    
    def __str__(self) -> str:
        tags_str = f", tags: {', '.join(self.tags_list())}" if self.tags_list() else ""
        content_preview = (self.content[:50] + "...") if len(self.content) > 50 else self.content
        return f"Note '{self.name}': {content_preview}{tags_str}"
    
    def __repr__(self) -> str:
        return f"Note(name={self.name!r}, content={self.content!r})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Note):
            return NotImplemented
        return self.name == other.name
    
    def __setstate__(self, state: dict):
        """Handle backward compatibility for unpickling older notes without tags."""
        self.__dict__.update(state)
        if "tags" not in self.__dict__:
            self.tags = Tags()
        if "name" not in self.__dict__ and "value" in self.__dict__:
            self.name = self.value


