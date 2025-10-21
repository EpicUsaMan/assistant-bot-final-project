"""Base field class for contact record fields."""


class Field:
    """
    Base class for contact record fields.
    
    Attributes:
        value: The field value
    """
    
    def __init__(self, value: str) -> None:
        """
        Initialize a field with a value.
        
        Args:
            value: The field value to store
        """
        self.value = value
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value!r})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Field):
            return NotImplemented
        return self.value == other.value

