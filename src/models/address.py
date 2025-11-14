"""Address class for contact records."""

from typing import Optional


class Address:
    """
    Class for storing contact address information.
    
    Address consists of country code, city name, and street address line.
    Provides formatted string representation and empty check.
    
    Attributes:
        country: Country code (e.g., "UA", "PL")
        city: City name
        address_line: Street address
    """
    
    def __init__(
        self,
        country: str,
        city: str,
        address_line: str,
    ) -> None:
        """
        Initialize an address with country, city, and street address.
        
        Args:
            country: Country code (e.g., "UA", "PL")
            city: City name
            address_line: Street address
        """
        self.country = country.strip() if country else None
        self.city = city.strip() if city else None
        self.address_line = address_line.strip() if address_line else None
    
    def is_empty(self) -> bool:
        """
        Check if address is empty (all fields are None or empty).
        
        Returns:
            True if all address fields are empty, False otherwise
        """
        return not (self.country or self.city or self.address_line)
    
    def __str__(self) -> str:
        """
        Return formatted address string.
        
        Format: "address_line, city, country"
        Only includes non-empty parts.
        
        Returns:
            Formatted address string or empty string if address is empty
        """
        parts = []
        if self.address_line:
            parts.append(self.address_line)
        if self.city:
            parts.append(self.city)
        if self.country:
            parts.append(self.country)
        
        return ", ".join(parts) if parts else ""
    
    def __repr__(self) -> str:
        return f"Address(country={self.country!r}, city={self.city!r}, address_line={self.address_line!r})"
    
    def __eq__(self, other: object) -> bool:
        """Check if two addresses are equal."""
        if not isinstance(other, Address):
            return NotImplemented
        return (
            self.country == other.country
            and self.city == other.city
            and self.address_line == other.address_line
        )

