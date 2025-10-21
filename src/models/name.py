"""Name field class for contact records."""

from src.models.field import Field


class Name(Field):
    """
    Class for storing contact name.
    
    This is a mandatory field for contact records.
    
    Attributes:
        value: The contact's name
    """
    
    def __init__(self, value: str) -> None:
        """
        Initialize a name field.
        
        Args:
            value: The contact's name
            
        Raises:
            ValueError: If name is empty or contains only whitespace
        """
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        super().__init__(value.strip())

