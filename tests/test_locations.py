"""Tests for locations catalog functionality."""

import json
import pytest
from pathlib import Path
from src.utils.locations import LocationsCatalog


@pytest.fixture
def temp_locations_file(tmp_path):
    """
    Create a temporary locations file for testing.
    
    Args:
        tmp_path: Pytest fixture providing temporary directory
        
    Returns:
        Path to temporary locations.json file
    """
    locations_file = tmp_path / "locations.json"
    
    # Create initial data structure
    initial_data = {
        "countries": {
            "UA": {
                "name": "Ukraine",
                "cities": ["Kyiv", "Lviv", "Odesa"]
            },
            "PL": {
                "name": "Poland",
                "cities": ["Warsaw", "Krakow"]
            }
        },
        "user_cities": {},
        "user_countries": {}
    }
    
    with open(locations_file, "w", encoding="utf-8") as f:
        json.dump(initial_data, f, ensure_ascii=False, indent=2)
    
    return locations_file


@pytest.fixture
def catalog(temp_locations_file):
    """
    Create a LocationsCatalog instance with temporary file.
    
    Args:
        temp_locations_file: Path to temporary locations file
        
    Returns:
        LocationsCatalog instance
    """
    return LocationsCatalog(catalog_path=temp_locations_file)


class TestLocationsCatalogCountries:
    """Test country-related functionality."""
    
    def test_get_countries_returns_predefined(self, catalog):
        """Test that get_countries returns predefined countries."""
        countries = catalog.get_countries(include_user=False)
        
        assert len(countries) == 2
        assert ("UA", "Ukraine") in countries
        assert ("PL", "Poland") in countries
    
    def test_get_countries_sorted_by_name(self, catalog):
        """Test that countries are sorted by name."""
        countries = catalog.get_countries()
        
        # Poland comes before Ukraine alphabetically
        assert countries[0][1] == "Poland"
        assert countries[1][1] == "Ukraine"
    
    def test_get_country_name_existing(self, catalog):
        """Test getting name of existing country."""
        name = catalog.get_country_name("UA")
        assert name == "Ukraine"
    
    def test_get_country_name_nonexistent(self, catalog):
        """Test getting name of non-existent country returns None."""
        name = catalog.get_country_name("XX")
        assert name is None
    
    def test_has_country_existing(self, catalog):
        """Test checking if country exists."""
        assert catalog.has_country("UA") is True
        assert catalog.has_country("PL") is True
    
    def test_has_country_nonexistent(self, catalog):
        """Test checking if non-existent country exists."""
        assert catalog.has_country("XX") is False
    
    def test_is_user_country_predefined(self, catalog):
        """Test that predefined countries are not marked as user countries."""
        assert catalog.is_user_country("UA") is False
        assert catalog.is_user_country("PL") is False


class TestLocationsCatalogUserCountries:
    """Test user-defined country functionality."""
    
    def test_add_user_country_valid(self, catalog):
        """Test adding a valid user country."""
        catalog.add_user_country("DE", "Germany")
        
        assert catalog.has_country("DE") is True
        assert catalog.get_country_name("DE") == "Germany"
        assert catalog.is_user_country("DE") is True
    
    def test_add_user_country_persists(self, catalog, temp_locations_file):
        """Test that added user country is saved to file."""
        catalog.add_user_country("DE", "Germany")
        
        # Read file directly
        with open(temp_locations_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert "DE" in data["user_countries"]
        assert data["user_countries"]["DE"]["name"] == "Germany"
        assert data["user_countries"]["DE"]["cities"] == []
    
    def test_add_user_country_empty_code(self, catalog):
        """Test that empty country code raises error."""
        with pytest.raises(ValueError, match="Country code cannot be empty"):
            catalog.add_user_country("", "Test")
    
    def test_add_user_country_empty_name(self, catalog):
        """Test that empty country name raises error."""
        with pytest.raises(ValueError, match="Country name cannot be empty"):
            catalog.add_user_country("XX", "")
    
    def test_add_user_country_invalid_code_format(self, catalog):
        """Test that invalid country code format raises error."""
        with pytest.raises(ValueError, match="Country code must be 2-3 letters"):
            catalog.add_user_country("X", "Test")
        
        with pytest.raises(ValueError, match="Country code must be 2-3 letters"):
            catalog.add_user_country("XXXX", "Test")
        
        with pytest.raises(ValueError, match="Country code must be 2-3 letters"):
            catalog.add_user_country("12", "Test")
    
    def test_add_user_country_duplicate_predefined(self, catalog):
        """Test that adding duplicate predefined country raises error."""
        with pytest.raises(ValueError, match="Country 'UA' already exists"):
            catalog.add_user_country("UA", "Ukraine Duplicate")
    
    def test_add_user_country_duplicate_user(self, catalog):
        """Test that adding duplicate user country raises error."""
        catalog.add_user_country("DE", "Germany")
        
        with pytest.raises(ValueError, match="Country 'DE' already exists"):
            catalog.add_user_country("DE", "Germany Duplicate")
    
    def test_add_user_country_normalizes_code(self, catalog):
        """Test that country code is normalized to uppercase."""
        catalog.add_user_country("de", "Germany")
        
        assert catalog.has_country("DE") is True
        assert catalog.get_country_name("DE") == "Germany"
    
    def test_get_user_countries(self, catalog):
        """Test getting only user-added countries."""
        catalog.add_user_country("DE", "Germany")
        catalog.add_user_country("FR", "France")
        
        user_countries = catalog.get_user_countries()
        
        assert len(user_countries) == 2
        assert ("DE", "Germany") in user_countries
        assert ("FR", "France") in user_countries
    
    def test_get_user_countries_sorted(self, catalog):
        """Test that user countries are sorted by name."""
        catalog.add_user_country("DE", "Germany")
        catalog.add_user_country("FR", "France")
        
        user_countries = catalog.get_user_countries()
        
        # France comes before Germany alphabetically
        assert user_countries[0][1] == "France"
        assert user_countries[1][1] == "Germany"
    
    def test_get_countries_includes_user_countries(self, catalog):
        """Test that get_countries includes user countries when requested."""
        catalog.add_user_country("DE", "Germany")
        
        all_countries = catalog.get_countries(include_user=True)
        
        assert len(all_countries) == 3
        assert ("DE", "Germany") in all_countries
    
    def test_get_countries_excludes_user_countries(self, catalog):
        """Test that get_countries excludes user countries when requested."""
        catalog.add_user_country("DE", "Germany")
        
        predefined_only = catalog.get_countries(include_user=False)
        
        assert len(predefined_only) == 2
        assert ("DE", "Germany") not in predefined_only


class TestLocationsCatalogCitiesWithUserCountries:
    """Test city functionality with user-defined countries."""
    
    def test_get_cities_for_user_country(self, catalog):
        """Test getting cities for a user-defined country."""
        catalog.add_user_country("DE", "Germany")
        
        cities = catalog.get_cities("DE")
        assert cities == []
    
    def test_add_city_to_user_country(self, catalog):
        """Test adding a city to a user-defined country."""
        catalog.add_user_country("DE", "Germany")
        catalog.add_user_city("DE", "Berlin")
        
        cities = catalog.get_cities("DE")
        assert "Berlin" in cities
    
    def test_get_cities_includes_user_country_cities(self, catalog):
        """Test that get_cities works with user countries."""
        catalog.add_user_country("DE", "Germany")
        catalog.add_user_city("DE", "Berlin")
        catalog.add_user_city("DE", "Munich")
        
        cities = catalog.get_cities("DE", include_user=True)
        
        assert len(cities) == 2
        assert "Berlin" in cities
        assert "Munich" in cities


class TestLocationsCatalogInitialization:
    """Test catalog initialization and persistence."""
    
    def test_init_creates_empty_structure_if_file_missing(self, tmp_path):
        """Test that initialization creates empty structure if file doesn't exist."""
        nonexistent_file = tmp_path / "nonexistent.json"
        catalog = LocationsCatalog(catalog_path=nonexistent_file)
        
        assert catalog.get_countries() == []
        assert catalog.get_user_countries() == []
    
    def test_init_ensures_user_countries_key_exists(self, tmp_path):
        """Test that initialization adds user_countries key if missing."""
        locations_file = tmp_path / "locations.json"
        
        # Create file without user_countries key
        data = {
            "countries": {},
            "user_cities": {}
        }
        
        with open(locations_file, "w", encoding="utf-8") as f:
            json.dump(data, f)
        
        catalog = LocationsCatalog(catalog_path=locations_file)
        
        # Should not raise error and should have empty user_countries
        assert catalog.get_user_countries() == []
    
    def test_reload_after_external_change(self, catalog, temp_locations_file):
        """Test that catalog can be reloaded after external changes."""
        # Add country through catalog
        catalog.add_user_country("DE", "Germany")
        
        # Create new catalog instance (simulating reload)
        new_catalog = LocationsCatalog(catalog_path=temp_locations_file)
        
        # Verify country persisted
        assert new_catalog.has_country("DE") is True
        assert new_catalog.get_country_name("DE") == "Germany"


class TestLocationsCatalogEdgeCases:
    """Test edge cases and error handling."""
    
    def test_add_user_country_with_whitespace(self, catalog):
        """Test that whitespace is stripped from country code and name."""
        catalog.add_user_country("  de  ", "  Germany  ")
        
        assert catalog.has_country("DE") is True
        assert catalog.get_country_name("DE") == "Germany"
    
    def test_get_country_name_checks_user_countries(self, catalog):
        """Test that get_country_name checks user countries."""
        catalog.add_user_country("DE", "Germany")
        
        name = catalog.get_country_name("DE")
        assert name == "Germany"
    
    def test_has_country_checks_both_predefined_and_user(self, catalog):
        """Test that has_country checks both predefined and user countries."""
        catalog.add_user_country("DE", "Germany")
        
        assert catalog.has_country("UA") is True  # Predefined
        assert catalog.has_country("DE") is True  # User
        assert catalog.has_country("XX") is False  # Non-existent

