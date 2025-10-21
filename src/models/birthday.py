"""Birthday field class for contact records with date validation."""

from datetime import datetime
from src.models.field import Field


class Birthday(Field):
    """
    Class for storing birthday date with validation.
    
    Birthday must be in DD.MM.YYYY format.
    
    Attributes:
        value: The validated birthday as datetime object
    """
    
    DATE_FORMAT = "%d.%m.%Y"
    
    def __init__(self, value: str) -> None:
        """
        Initialize a birthday field with validation.
        
        Args:
            value: The birthday string in DD.MM.YYYY format
            
        Raises:
            ValueError: If date format is invalid or date doesn't exist
        """
        date_obj = self._validate(value)
        super().__init__(value)
        self._date = date_obj
    
    def _validate(self, value: str) -> datetime:
        """
        Validate birthday format and convert to datetime.
        
        Args:
            value: The birthday string to validate
            
        Returns:
            datetime object representing the birthday
            
        Raises:
            ValueError: If format is invalid or date doesn't exist
        """
        try:
            date_obj = datetime.strptime(value, self.DATE_FORMAT)
            return date_obj
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
    
    @property
    def date(self) -> datetime:
        """
        Get birthday as datetime object.
        
        Returns:
            datetime object representing the birthday
        """
        return self._date
    
    def __str__(self) -> str:
        return self.value






