"""Phone field class for contact records with validation."""

from src.models.field import Field


class Phone(Field):
    """
    Class for storing phone number with validation.
    
    Phone numbers must be exactly 10 digits.
    
    Attributes:
        value: The validated phone number
    """
    
    def __init__(self, value: str) -> None:
        """
        Initialize a phone field with validation.
        
        Args:
            value: The phone number string
            
        Raises:
            ValueError: If phone number is not exactly 10 digits
        """
        self._validate(value)
        super().__init__(value)
    
    def _validate(self, value: str) -> None:
        """
        Validate phone number format.
        
        Args:
            value: The phone number to validate
            
        Raises:
            ValueError: If phone number is not exactly 10 digits
        """
        if not value.isdigit():
            raise ValueError("Phone number must contain only digits")
        if len(value) != 10:
            raise ValueError("Phone number must be exactly 10 digits")

