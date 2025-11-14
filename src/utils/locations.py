"""
Utilities for working with country and city catalog.

This module provides functions for loading, searching, and managing
the locations catalog (countries and cities) from JSON file.
"""

import json
from pathlib import Path
from typing import Optional

# Path to locations catalog
LOCATIONS_FILE = Path(__file__).parent.parent / "data" / "locations.json"


class LocationsCatalog:
    """
    Catalog manager for countries and cities.
    
    Handles loading, searching, and adding user-defined cities.
    Separates predefined cities from user-added ones for audit purposes.
    """
    
    def __init__(self, catalog_path: Path = LOCATIONS_FILE) -> None:
        """
        Initialize catalog from JSON file.
        
        Args:
            catalog_path: Path to locations.json file
        """
        self.catalog_path = catalog_path
        self._data: dict = {}
        self._load()
    
    def _load(self) -> None:
        """Load catalog from JSON file."""
        try:
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        except FileNotFoundError:
            # If file doesn't exist, create empty structure
            self._data = {"countries": {}, "user_cities": {}}
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in locations file: {e}") from e
    
    def _save(self) -> None:
        """Save catalog to JSON file."""
        self.catalog_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.catalog_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
    
    def get_countries(self) -> list[tuple[str, str]]:
        """
        Get list of all countries as (country_code, country_name) tuples.
        
        Returns:
            List of tuples sorted by country name
        """
        countries = [
            (code, info["name"])
            for code, info in self._data.get("countries", {}).items()
        ]
        return sorted(countries, key=lambda x: x[1])
    
    def get_country_name(self, country_code: str) -> Optional[str]:
        """
        Get country name by country code.
        
        Args:
            country_code: ISO country code (e.g., "UA", "PL")
            
        Returns:
            Country name or None if not found
        """
        country = self._data.get("countries", {}).get(country_code)
        return country.get("name") if country else None
    
    def has_country(self, country_code: str) -> bool:
        """
        Check if country exists in catalog.
        
        Args:
            country_code: ISO country code
            
        Returns:
            True if country exists
        """
        return country_code in self._data.get("countries", {})
    
    def get_cities(self, country_code: str, include_user: bool = True) -> list[str]:
        """
        Get list of cities for a country.
        
        Args:
            country_code: ISO country code
            include_user: If True, include user-added cities
            
        Returns:
            List of city names (predefined first, then user-added if include_user=True)
        """
        if not self.has_country(country_code):
            return []
        
        predefined = self._data["countries"][country_code].get("cities", [])
        
        if not include_user:
            return sorted(predefined)
        
        user_cities = self._data.get("user_cities", {}).get(country_code, [])
        all_cities = predefined + user_cities
        return sorted(set(all_cities))  # Remove duplicates, sort
    
    def search_cities(self, country_code: str, query: str) -> list[str]:
        """
        Search cities by partial name match (case-insensitive).
        
        Args:
            country_code: ISO country code
            query: Search query (partial city name)
            
        Returns:
            List of matching city names (sorted)
        """
        cities = self.get_cities(country_code, include_user=True)
        query_lower = query.lower().strip()
        
        if not query_lower:
            return cities
        
        matches = [
            city for city in cities
            if query_lower in city.lower()
        ]
        return sorted(matches)
    
    def add_user_city(self, country_code: str, city_name: str) -> None:
        """
        Add a user-defined city to the catalog.
        
        Args:
            country_code: ISO country code
            city_name: City name to add
            
        Raises:
            ValueError: If country doesn't exist or city already exists
        """
        if not self.has_country(country_code):
            raise ValueError(f"Country '{country_code}' not found in catalog")
        
        city_name = city_name.strip()
        if not city_name:
            raise ValueError("City name cannot be empty")
        
        # Check if city already exists (predefined or user-added)
        predefined = self._data["countries"][country_code].get("cities", [])
        if city_name in predefined:
            raise ValueError(f"City '{city_name}' already exists in predefined list")
        
        # Initialize user_cities if needed
        if "user_cities" not in self._data:
            self._data["user_cities"] = {}
        
        if country_code not in self._data["user_cities"]:
            self._data["user_cities"][country_code] = []
        
        # Check if already in user cities
        if city_name in self._data["user_cities"][country_code]:
            raise ValueError(f"City '{city_name}' already exists in user cities")
        
        # Add to user cities
        self._data["user_cities"][country_code].append(city_name)
        self._save()
    
    def get_user_cities(self, country_code: str) -> list[str]:
        """
        Get only user-added cities for a country (for audit purposes).
        
        Args:
            country_code: ISO country code
            
        Returns:
            List of user-added city names
        """
        return sorted(self._data.get("user_cities", {}).get(country_code, []))
    
    def is_user_city(self, country_code: str, city_name: str) -> bool:
        """
        Check if city is user-added (not predefined).
        
        Args:
            country_code: ISO country code
            city_name: City name to check
            
        Returns:
            True if city is user-added
        """
        user_cities = self._data.get("user_cities", {}).get(country_code, [])
        return city_name in user_cities


# Global catalog instance (singleton pattern)
_catalog_instance: Optional[LocationsCatalog] = None


def get_catalog() -> LocationsCatalog:
    """
    Get global catalog instance (singleton).
    
    Returns:
        LocationsCatalog instance
    """
    global _catalog_instance
    if _catalog_instance is None:
        _catalog_instance = LocationsCatalog()
    return _catalog_instance


def reload_catalog() -> None:
    """Reload catalog from file (useful after external changes)."""
    global _catalog_instance
    _catalog_instance = None

