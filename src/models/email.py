"""Email field class for contact records with validation."""

from src.models.field import Field
from src.utils.validators import _validate_email_format


class Email(Field):
    """
    Class for storing email address with validation.
    
    Email is normalized to lowercase and validated for format.
    Uses shared validation logic from validators module.
    
    Attributes:
        value: The validated and normalized email address (lowercase)
    """
    
    def __init__(self, value: str) -> None:
        """
        Initialize an email field with validation.
        
        Args:
            value: The email address string
            
        Raises:
            ValueError: If email format is invalid
        """
        normalized = _validate_email_format(value)
        super().__init__(normalized)
    
    def __str__(self) -> str:
        return self.value

