# Assistant Bot - Modern Contact Manager

![Coverage](./coverage.svg)

A professional console-based contact management system built with **MVCS architecture**, **Dependency Injection**, and **modern Python best practices**. Features interactive REPL mode, beautiful terminal UI, comprehensive validation, and automatic data persistence.

**Tech Stack:** Python 3.10+ • Typer • Rich • Click-REPL • Dependency Injector • Pytest

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Available Commands](#available-commands)
- [Project Structure](#project-structure)
- [Architecture: MVCS Pattern](#architecture-mvcs-pattern)
- [Data Models](#data-models)
- [Services](#services)
- [Utilities](#utilities)
- [Testing](#testing)
- [Data Validation](#data-validation)
- [Data Persistence](#data-persistence)
- [Adding New Features](#adding-new-features)
- [Development](#development)
- [Contributing](#contributing)

## Python Version

Python 3.10 or higher required

## Features

### Architecture & Design
- **MVCS Pattern** (Model-View-Controller-Service) with clear separation of concerns
- **Dependency Injection** for better testability and maintainability
- **Commands ARE Controllers** that also handle presentation (no separate controller layer)
- **Auto-registration** of commands - just add a new file in `src/commands/`
- **Comprehensive test coverage** with pytest and coverage reporting

### User Experience
- **Interactive REPL mode** powered by click-repl for conversational usage
- **CLI mode** for single-command execution and scripting
- **Beautiful terminal UI** with Rich library formatting
- **Two-tier validation** with user-friendly error messages
- **Automatic data persistence** via decorators (no manual saves)

### Technical Features
- **Standardized command patterns** with validators and decorators
- **Clean error handling** with REPL-aware behavior
- **Type hints** throughout codebase
- **Pickle-based persistence** with automatic serialization
- **Comprehensive documentation** with examples
- Tagging: per-contact tags, tag-based search (AND/OR), and tag-aware sorting

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```bash
# Start interactive mode
python src/main.py

# Or use CLI mode for single commands
python src/main.py add "John Doe" 1234567890
python src/main.py add-birthday "John Doe" 15.05.1990
python src/main.py all
python src/main.py all --sort-by name
python src/main.py all --sort-by tag_count
python src/main.py all --sort-by tag_name
python src/main.py birthdays
```

## Dependencies
- **typer** (>=0.12) - Modern CLI framework
- **click** (>=8.1) - Command-line interface creation kit
- **click-repl** (>=0.3) - REPL plugin for Click
- **rich** (>=13.7) - Beautiful terminal formatting
- **dependency-injector** (>=4.41) - Dependency injection framework
- **pytest** (>=8.0.0) - Testing framework
- **pytest-cov** (>=4.0.0) - Test coverage plugin
- **coverage-badge** (>=1.1.0) - Generate coverage badges

## Usage

### Interactive Mode (REPL)

Launch the interactive mode for a conversational experience:

```bash
python src/main.py
```

Or explicitly:

```bash
python src/main.py interactive
```

### Command-Line Mode

Execute single commands directly:

```bash
# View all commands
python src/main.py --help

# Add a contact
python src/main.py add "John Doe" 1234567890

# Show all contacts
python src/main.py all

# Show all contacts sorted
python src/main.py all --sort-by name
python src/main.py all --sort-by phone
python src/main.py all --sort-by birthday
python src/main.py all --sort-by tag_count
python src/main.py all --sort-by tag_name

# Add a birthday
python src/main.py add-birthday "John Doe" 15.05.1990

# Show upcoming birthdays
python src/main.py birthdays
```
### Tags

Rules: tags are lowercase, unique per contact; allowed `[a-z0-9_-]`, length `1..32`.

```bash
# CRUD
python src/main.py tag-add "John Doe" ml
# Multiple tags (args)
python src/main.py tag-add "John" ml ai
# Comma inside a quoted tag
python src/main.py tag-add "John" "data,science"
python src/main.py tag-list "John Doe"
python src/main.py tag-remove "John Doe" ml
python src/main.py tag-clear "John Doe"

# Search
python src/main.py find-by-tags "ai,ml"        # AND
python src/main.py find-by-tags-any "ai,ml"    # OR
# Search with CSV + quotes
python src/main.py find-by-tags "data,science" ml
python src/main.py find-by-tags-any ml ai

# List sorting by tags and other fields
python src/main.py all --sort-by name
python src/main.py all --sort-by phone
python src/main.py all --sort-by birthday
python src/main.py all --sort-by tag_count
python src/main.py all --sort-by tag_name

## Available Commands

| Command | Arguments | Description |
|---------|-----------|-------------|
| `hello` | None | Get a greeting from the bot |
| `add` | name, phone | Add a new contact or add phone to existing contact |
| `change` | name, old_phone, new_phone | Change an existing phone number |
| `phone` | name | Show all phone numbers for a contact |
| `all` | `[--sort-by MODE]` | Show all contacts in the address book (optionally sorted by `name`, `phone`, `birthday`, `tag_count`, or `tag_name`) |
| `add-birthday` | name, birthday (DD.MM.YYYY) | Add a birthday date to a contact |
| `show-birthday` | name | Show the birthday date for a contact |
| `birthdays` | None | Show all upcoming birthdays for the next week |
| `tag-add`            | name, tag                             | Add a tag to a contact                                   |
| `tag-remove`         | name, tag                             | Remove a tag from a contact                              |
| `tag-list`           | name                                  | List tags of a contact                                   |
| `tag-clear`          | name                                  | Clear all tags for a contact                             |
| `find-by-tags`       | "t1,t2"                               | Find contacts that have **ALL** tags (AND)               |
| `find-by-tags-any`   | "t1,t2"                               | Find contacts that have **ANY** tag (OR)                 |
| `interactive` | None | Start interactive REPL mode |

## Project Structure

```
.
├── README.md
├── requirements.txt
├── coverage.svg                   # Test coverage badge
├── .coveragerc                    # Coverage configuration
├── src/
│   ├── __init__.py
│   ├── main.py                    # Main CLI entry point with auto-registration and interactive mode
│   ├── container.py               # Dependency injection container
│   ├── commands/                  # Individual command implementations (Controller + View)
│   │   ├── __init__.py
│   │   ├── add.py                 # Add contact command
│   │   ├── change.py              # Change phone command
│   │   ├── phone.py               # Show phone command
│   │   ├── all.py                 # Show all contacts command
│   │   ├── add_birthday.py        # Add birthday command
│   │   ├── show_birthday.py       # Show birthday command
│   │   ├── birthdays.py           # Show upcoming birthdays command
│   │   ├── hello.py               # Greeting command
│   │   ├── tags.py                # Tag CRUD commands
│   │   ├── find_by_tags.py        # AND search by tags
│   │   └── find_by_tags_any.py    # OR search by tags
│   ├── models/                    # Data models with validation and serialization
│   │   ├── __init__.py
│   │   ├── field.py               # Base field class
│   │   ├── name.py                # Name field
│   │   ├── phone.py               # Phone field with validation
│   │   ├── birthday.py            # Birthday field with validation
│   │   ├── record.py              # Contact record
│   │   ├── tags.py                # Tags value object (normalize/validate, set ops)
│   │   └── address_book.py        # Address book with persistence
│   ├── services/                  # Business logic services
│   │   ├── __init__.py
│   │   └── contact_service.py     # Contact management service
│   └── utils/                     # Utilities for commands
│       ├── __init__.py
│       ├── validators.py          # CLI parameter validators
│       └── command_decorators.py  # Error handling and auto-save decorators
└── tests/                         # Comprehensive test suite
    ├── __init__.py
    ├── test_field.py
    ├── test_name.py
    ├── test_phone.py
    ├── test_birthday.py
    ├── test_record.py
    ├── test_address_book.py
    ├── test_contact_service.py
    ├── test_commands.py
    ├── test_validators.py
    └── test_container.py
```

## Architecture: MVCS Pattern

This project follows the **Model-View-Controller-Service (MVCS)** architecture pattern:

### MVCS Layers

```
Command (Controller + View)
       ↓
   Service
       ↓
    Model
```

1. **Model Layer** (`src/models/`)
   - Data structures and data access
   - Handle data validation
   - Manage serialization/deserialization
   - Examples: Field, Name, Phone, Birthday, Record, AddressBook

2. **Service Layer** (`src/services/`)
   - Business logic
   - Coordinate model operations
   - Return simple data types or raise exceptions
   - Example: ContactService

3. **Command Layer** (`src/commands/`) - **Controller + View**
   - Commands ARE controllers in this architecture
   - Handle user input (via Typer)
   - Call service methods
   - Handle exceptions from services
   - Format and display results (using Rich)
   - Examples: add.py, change.py, phone.py

### Dependency Injection

The application uses the `dependency-injector` framework for managing dependencies:

```python
# Container definition (src/container.py)
class Container(containers.DeclarativeContainer):
    # Address book model (singleton - handles its own persistence)
    address_book = providers.Singleton(
        lambda filename: AddressBook.load_from_file(filename),
        filename=config.storage.filename.as_(str)
    )
    
    # Contact service (factory - business logic)
    contact_service = providers.Factory(ContactService, ...)
```

**Dependency Hierarchy:**
- Commands inject Services (not controllers)
- Services inject Models
- Models handle their own persistence

### Auto-Registration of Commands

Commands are automatically discovered and registered - no manual imports needed!

```python
# Just create a new file in src/commands/ with an 'app' attribute
# Example: src/commands/my_command.py
import typer
from dependency_injector.wiring import inject, Provide
from rich.console import Console
from src.container import Container
from src.services.contact_service import ContactService

app = typer.Typer()
console = Console()

@app.command(name="my-command")
@inject
def my_command_function(
    contact_service: ContactService = Provide[Container.contact_service]
):
    """
    My command description.
    
    This command acts as both Controller and View:
    - Controller: Handles exceptions and coordinates service calls
    - View: Formats and displays results using Rich
    """
    try:
        # Call service (business logic)
        result = contact_service.some_method()
        # Display result (view logic)
        console.print(f"[green]{result}[/green]")
    except ValueError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
```

The main application automatically discovers and registers it!

## Data Models

### Field
Base class for all contact record fields with value validation.

**Attributes:**
- `value: str` - The field value

**Purpose:** Provides common interface for all field types (Name, Phone, Birthday).

### Name
Contact name field (inherits from Field).

**Attributes:**
- `value: str` - Contact's name

**Validation:** Cannot be empty or contain only whitespace.

### Phone
Phone number field with validation (inherits from Field).

**Attributes:**
- `value: str` - Phone number (exactly 10 digits)

**Validation:** Must be exactly 10 digits containing only numeric characters.

### Birthday
Birthday field with date validation (inherits from Field).

**Attributes:**
- `value: str` - Birthday in DD.MM.YYYY format
- `date: datetime` - Parsed datetime object

**Validation:** Must be valid date in DD.MM.YYYY format.

### Record
Complete contact information with name, phones list, and optional birthday.

**Attributes:**
- `name: Name` - Contact's name (required)
- `phones: list[Phone]` - List of phone numbers (can be empty)
- `birthday: Optional[Birthday]` - Contact's birthday (optional)
- `tags: Tags` — contact tags container

**Methods:**
- `add_phone(phone: str) -> None` - Add a phone number
- `remove_phone(phone: str) -> None` - Remove a phone number
- `edit_phone(old_phone: str, new_phone: str) -> None` - Edit an existing phone number
- `find_phone(phone: str) -> Optional[Phone]` - Find a specific phone number
- `add_birthday(birthday: str) -> None` - Add a birthday in DD.MM.YYYY format
- `set_tags(tags: list[str] | str) -> None`
- `add_tag(tag: str) -> None`
- `remove_tag(tag: str) -> None`
- `clear_tags() -> None`
- `tags_list() -> list[str]`

**Backward compatibility:**
- Older pickles without `tags` are supported (added at load time).

**String Representation:**
Returns formatted string: `"Contact name: {name}, phones: {phones}, birthday: {birthday}"`

### Tags
Value object that stores a normalized, unique set of tags.

- Normalization: lowercase + trim
- Allowed charset: `[a-z0-9_-]`
- Length: `1..32`
- API: `add`, `remove`, `replace`, `clear`, `as_list`

### AddressBook
Stores and manages contact records (extends UserDict for dictionary-like interface).

**Attributes:**
- `data: dict[str, Record]` - Dictionary storing contact records (inherited from UserDict)

**Methods:**
- `add_record(record: Record) -> None` - Add a contact record
- `find(name: str) -> Optional[Record]` - Find a contact by name
- `delete(name: str) -> None` - Delete a contact
- `save_to_file(filename: str = "addressbook.pkl") -> None` - Save to file using pickle
- `load_from_file(filename: str = "addressbook.pkl") -> AddressBook` - Load from file (class method)

**Persistence:** Models handle their own serialization/deserialization using pickle.

## Services

### ContactService
Service layer encapsulating all business logic for contact operations. Injected into commands via the DI container.

**Constructor:**
- `__init__(address_book: AddressBook) -> None` - Initialize with address book dependency

**Public Methods:**

**Contact Management:**
- `add_contact(name: str, phone: str) -> str` - Add new contact or add phone to existing contact
  - Returns: Success message ("Contact added." or "Contact updated.")
  - Raises: `ValueError` if phone format is invalid

- `change_contact(name: str, old_phone: str, new_phone: str) -> str` - Change existing phone number
  - Returns: Success message "Contact updated."
  - Raises: `ValueError` if contact not found or phone invalid

- `get_phone(name: str) -> str` - Get all phone numbers for a contact
  - Returns: Phone numbers separated by semicolons or "No phones" message
  - Raises: `ValueError` if contact not found

- `get_all_contacts(sort_by: ContactSortBy | None = None) -> str` - Get all contacts as formatted string
  - Args: `sort_by` – optional sorting mode
  - Returns: Formatted string with all contacts or "No contacts in the address book."

**Tag Management:**
- `add_tag(name: str, tag: str) -> str`
- `remove_tag(name: str, tag: str) -> str`
- `clear_tags(name: str) -> str`
- `list_tags(name: str) -> list[str]`

**Tag Search:**
- `find_by_tags_all(tags: list[str] | str) -> list[tuple[name, Record]]` — AND
- `find_by_tags_any(tags: list[str] | str) -> list[tuple[name, Record]]` — OR

ContactService uses `ContactSortBy` enum for sorting modes.

**Listing with sorting:**
- `list_contacts(sort_by: ContactSortBy | None = None) -> list[tuple[name, Record]]`  
  Where `ContactSortBy` is an enum with values:
  - `name` – sort by contact name (alphabetically, case-insensitive)
  - `phone` – sort by first phone number
  - `birthday` – sort by birthday date (contacts without birthday go last)
  - `tag_count` – sort by number of tags (descending)
  - `tag_name` – sort by tag names (contacts without tags go first)

**Birthday Management:**
- `add_birthday(name: str, birthday: str) -> str` - Add birthday to contact
  - Args: birthday in DD.MM.YYYY format
  - Returns: Success message "Birthday added."
  - Raises: `ValueError` if contact not found or date format invalid

- `get_birthday(name: str) -> str` - Get birthday for a contact
  - Returns: Birthday date or "No birthday set" message
  - Raises: `ValueError` if contact not found

- `get_upcoming_birthdays(days: int = 7) -> str` - Get upcoming birthdays
  - Args: Number of days to look ahead (default: 7)
  - Returns: Formatted list of upcoming birthdays or "No upcoming birthdays" message
  - Note: Automatically adjusts weekend birthdays to Monday

**Utility Methods:**
- `has_contacts() -> bool` - Check if address book has any contacts

**Private Methods:**
- `_calculate_upcoming_birthdays(days: int = 7) -> list[dict]` - Calculate upcoming birthdays with weekend adjustment
  - Returns: List of dicts with 'name' and 'congratulation_date' keys

**Design Principles:**
- Returns simple types (str, bool, list) for easy display
- Raises exceptions for error conditions (caught by command decorators)
- Contains NO presentation logic (no Rich formatting)
- All business logic lives here (not in commands or models)

## Utilities

### Validators (`src/utils/validators.py`)
CLI parameter validators used as Typer callbacks for input validation at the parameter level.

**Available Validators:**
- `validate_phone(value: str) -> str` - Validates phone number format (exactly 10 digits)
  - Raises: `typer.BadParameter` with user-friendly message

- `validate_birthday(value: str) -> str` - Validates birthday date format (DD.MM.YYYY)
  - Raises: `typer.BadParameter` with user-friendly message

- `validate_email(value: str) -> str` - Validates email format (basic validation)
  - Raises: `typer.BadParameter` with user-friendly message

**Usage:**
```python
@app.command()
def add_command(
    phone: str = typer.Argument(..., callback=validate_phone),
):
    ...
```

**Benefits:**
- Typer shows which parameter failed validation
- Consistent error messages across all commands
- Validation happens before service layer is called

### Command Decorators (`src/utils/command_decorators.py`)
Decorators providing standardized error handling and auto-save functionality.

**Available Decorators:**

**`@handle_service_errors`** - Error handling for service layer exceptions
- Catches `ValueError` and `KeyError` from services/models
- Displays user-friendly error messages with Rich formatting
- In REPL mode: displays error but continues session
- In CLI mode: displays error and exits with code 1
- Use on ALL commands (both READ and UPDATE)

**`@auto_save`** - Automatic data persistence after UPDATE operations
- Automatically saves address book after successful command execution
- Calls `address_book.save_to_file(filename)` automatically
- Use ONLY on UPDATE commands (add, change, add_birthday)
- Do NOT use on READ commands (phone, all, birthdays, show_birthday)

**Decorator Order:**
```python
@inject                    # 1. Dependency injection (must be first)
@handle_service_errors     # 2. Error handling
@auto_save                 # 3. Auto-save (UPDATE commands only)
def _command_impl(...):
    ...
```

**Benefits:**
- No repetitive try/except blocks in commands
- Consistent error handling across all commands
- Automatic data persistence (no manual save calls)
- Clear separation between READ and UPDATE operations

## Testing

The project includes comprehensive tests for all components with high code coverage.

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=src
```

### Generate Coverage Report
```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Generate coverage badge
coverage-badge -o coverage.svg -f
```

### Run Specific Test Suite
```bash
# Test models
pytest tests/test_field.py
pytest tests/test_name.py
pytest tests/test_phone.py
pytest tests/test_birthday.py
pytest tests/test_record.py
pytest tests/test_address_book.py

# Test services
pytest tests/test_contact_service.py

# Test commands
pytest tests/test_commands.py

# Test utilities
pytest tests/test_validators.py

# Test container
pytest tests/test_container.py
```

### Test Coverage
The project maintains high test coverage across all layers:
- **Models**: Complete coverage of data structures and validation
- **Services**: Complete coverage of business logic
- **Commands**: Complete coverage of CLI commands and error handling
- **Utilities**: Complete coverage of validators and decorators
- **Container**: Complete coverage of dependency injection

Coverage badge is automatically generated and displayed at the top of this README.

## Data Validation

The assistant bot implements two-tier validation for robust data integrity:

### Tier 1: CLI Parameter Validation (Typer Callbacks)
Input validation happens at the CLI parameter level using validators from `src/utils/validators.py`:

1. **Phone numbers** (`validate_phone`):
   - Must be exactly 10 digits
   - Must contain only numeric characters
   - Error shows which parameter failed: `Invalid value for 'PHONE': ...`

2. **Birthday dates** (`validate_birthday`):
   - Must be in DD.MM.YYYY format
   - Must represent a valid date
   - Error shows which parameter failed: `Invalid value for 'BIRTHDAY': ...`

3. **Email addresses** (`validate_email`):
   - Must contain `@` and `.`
   - Basic format validation (ready for future use)

4. **Tags**:
   - Allowed pattern: `^[a-z0-9_-]{1,32}$`
   - Normalized to lowercase
   - Duplicates removed per contact

**Benefits:**
- Users immediately see which parameter is invalid
- Validation happens before service layer is called
- Consistent error messages across all commands

### Tier 2: Model Validation
Additional validation happens at the model level for data integrity:

1. **Field class**: Base validation for all field types
2. **Name field**: Cannot be empty or contain only whitespace
3. **Phone field**: Validates 10-digit format (defense in depth)
4. **Birthday field**: Validates DD.MM.YYYY format and parses to datetime
5. **Record class**: 
   - Prevents duplicate phones
   - Validates phone exists before removal/edit
6. **AddressBook class**:
   - Prevents duplicate contact names
   - Validates record exists before deletion

**Error Handling:**
All validation errors are caught by the `@handle_service_errors` decorator and displayed as user-friendly messages with Rich formatting. In REPL mode, errors don't exit the session; in CLI mode, they exit with code 1.

## Data Persistence

The application uses a sophisticated persistence strategy with automatic saving:

### Loading Data
- Address book is loaded on startup from `addressbook.pkl`
- Uses `AddressBook.load_from_file()` class method
- If file doesn't exist, creates new empty address book
- File location configured in DI container: `Container.config.storage.filename`

### Saving Data
- Data automatically saved after UPDATE operations via `@auto_save` decorator
- UPDATE commands (add, change, add_birthday) have `@auto_save` applied
- READ commands (phone, all, birthdays, show_birthday) do NOT save
- Uses Python's pickle serialization
- Models handle their own persistence (serialization/deserialization)

### Storage Format
- **File format**: Binary pickle file (`.pkl`)
- **Default location**: `addressbook.pkl` in project root
- **Serialized object**: Complete `AddressBook` instance with all records
- **Benefits**: 
  - Fast serialization/deserialization
  - Preserves complete object graph
  - No manual schema management

### Configuration
File location can be configured in `src/main.py`:
```python
container.config.storage.filename.from_value("addressbook.pkl")
```

Or via environment variables or config files using dependency-injector's configuration system.

## Examples

### Interactive Mode

```bash
$ python src/main.py

╭─────────────── Assistant Bot ───────────────╮
│ Welcome to the Assistant Bot!               │
│                                             │
│ Available commands:                         │
│   • hello - Get a greeting                  │
│   • add [name] [phone] - Add a contact      │
│   • ...                                     │
╰─────────────────────────────────────────────╯

> add John 1234567890
Contact added.

> add-birthday John 15.05.1990
Birthday added.

> all
╭────────────── All Contacts ──────────────╮
│ Contact name: John, phones: 1234567890,  │
│ birthday: 15.05.1990                     │
╰──────────────────────────────────────────╯

> exit
Good bye!
```

### Command-Line Mode

```bash
# Add contacts
python src/main.py add Alice 5551234567
python src/main.py add Bob 5559876543

# Add birthdays
python src/main.py add-birthday Alice 10.03.1995
python src/main.py add-birthday Bob 25.12.1990

# View all contacts
python src/main.py all

# View upcoming birthdays
python src/main.py birthdays
```

## Adding New Features

### Adding a New Command

Adding a new command is simple thanks to auto-registration:

1. **Create command file** in `src/commands/`, e.g., `src/commands/search.py`

2. **Define the command** using the standard pattern:

```python
import typer
from dependency_injector.wiring import inject, Provide
from rich.console import Console
from src.container import Container
from src.services.contact_service import ContactService
from src.utils.command_decorators import handle_service_errors, auto_save

app = typer.Typer()
console = Console()

# For UPDATE commands (that modify data):
@inject
@handle_service_errors
@auto_save  # Include this for UPDATE commands
def _search_impl(
    query: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation with service logic."""
    # Call service method
    results = service.search_contacts(query)
    # Display results with Rich formatting
    console.print(f"[bold green]Found: {results}[/bold green]")

@app.command(name="search")
def search_command(
    query: str = typer.Argument(..., help="Search query"),
):
    """Search for contacts by name or phone."""
    return _search_impl(query)
```

3. **Add to wiring** in `src/main.py`:

```python
container.wire(modules=[
    # ... existing modules
    "src.commands.search",
])
```

4. **That's it!** The command is automatically registered and available in both REPL and CLI modes.

### Adding a New Service Method

To add business logic:

1. **Add method** to `src/services/contact_service.py`:

```python
def search_contacts(self, query: str) -> str:
    """
    Search for contacts by name or phone.
    
    Args:
        query: Search query string
        
    Returns:
        Formatted search results
        
    Raises:
        ValueError: If no contacts found
    """
    # Business logic here
    results = []
    for record in self.address_book.data.values():
        if query.lower() in record.name.value.lower():
            results.append(str(record))
    
    if not results:
        raise ValueError(f"No contacts found matching '{query}'")
    
    return "\n".join(results)
```

2. **Add tests** to `tests/test_contact_service.py`

### Adding a New Validator

To add parameter validation:

1. **Create validator** in `src/utils/validators.py`:

```python
def validate_email(value: str) -> str:
    """Validate email format."""
    if "@" not in value or "." not in value:
        raise typer.BadParameter("Invalid email format")
    return value
```

2. **Use in command**:

```python
@app.command()
def add_email(
    email: str = typer.Argument(..., callback=validate_email),
):
    ...
```

3. **Add tests** to `tests/test_validators.py`

## Command Standardization

This project uses standardized patterns for commands to ensure consistency and reduce errors.

### Three Core Patterns

**1. Parameter Validation (Typer Callbacks)**

Validate input at the CLI level with clear error messages:

```python
from src.utils.validators import validate_phone, validate_birthday

@app.command()
def add_command(
    phone: str = typer.Argument(..., callback=validate_phone),  # Validates format
):
    ...
```

**Available validators:** `validate_phone`, `validate_birthday`, `validate_email`

Users see which parameter failed: `Invalid value for 'PHONE': Phone number must be exactly 10 digits`

**2. Error Handling (Decorator)**

Catch service errors without try/except blocks:

```python
from src.utils.command_decorators import handle_service_errors

@inject
@handle_service_errors  # Catches ValueError, KeyError from services
def _phone_impl(...):
    message = service.get_phone(name)  # No try/except needed
    console.print(message)
```

In REPL mode, errors are displayed but don't exit the session. In CLI mode, errors exit with code 1.

**3. Auto-Save (UPDATE Commands Only)**

Automatically persist data after modifications:

```python
from src.utils.command_decorators import auto_save

@inject
@handle_service_errors
@auto_save  # Saves data automatically after success
def _add_impl(name, phone, service, filename):
    message = service.add_contact(name, phone)
    console.print(message)
    # Data saved automatically - no manual save needed!
```

### Command Template

**UPDATE Command** (modifies data):
```python
from src.utils.validators import validate_phone
from src.utils.command_decorators import handle_service_errors, auto_save

@inject
@handle_service_errors
@auto_save
def _add_impl(name, phone, service, filename):
    message = service.add_contact(name, phone)
    console.print(f"[bold green]{message}[/bold green]")

@app.command()
def add_command(
    name: str = typer.Argument(...),
    phone: str = typer.Argument(..., callback=validate_phone),
):
    return _add_impl(name, phone)
```

**READ Command** (only reads data):
```python
from src.utils.command_decorators import handle_service_errors

@inject
@handle_service_errors  # No @auto_save for READ commands
def _phone_impl(name, service):
    message = service.get_phone(name)
    console.print(f"[bold cyan]{message}[/bold cyan]")

@app.command()
def phone_command(name: str = typer.Argument(...)):
    return _phone_impl(name)
```

### Adding New Validators

Create validator in `src/utils/validators.py`:

```python
def validate_email(value: str) -> str:
    if "@" not in value:
        raise typer.BadParameter("Invalid email format")
    return value
```

Use in command:
```python
email: str = typer.Argument(..., callback=validate_email)
```

### Code Review Checklist

- [ ] Parameters validated with callbacks?
- [ ] `@handle_service_errors` decorator present?
- [ ] UPDATE commands have `@auto_save`?
- [ ] READ commands do NOT have `@auto_save`?
- [ ] Decorator order: `@inject` → `@handle_service_errors` → `@auto_save`

## Development

### Code Standards
- **Type hints**: All functions and methods have complete type annotations
- **Docstrings**: Every class and function documented with Args, Returns, Raises
- **English only**: All comments and documentation in English
- **PEP 8 compliance**: Consistent code formatting
- **Low complexity**: Simple, readable code with shallow nesting
- **Meaningful names**: Clear, descriptive variable and function names

### Architecture Principles (MVCS)

**Separation of Concerns:**
- **Models** (`src/models/`): Data structures, validation, serialization
- **Services** (`src/services/`): Business logic, returns simple types, raises exceptions
- **Commands** (`src/commands/`): Controller + View - coordination, exception handling, presentation
- **Utilities** (`src/utils/`): Validators and decorators for cross-cutting concerns

**Dependency Injection:**
- All dependencies injected via `dependency-injector`
- No direct instantiation of dependencies in classes
- Container manages all object lifecycles
- Easy to mock for testing

**Key Principles:**
- **Commands ARE Controllers**: No separate controller layer needed
- **Models Own Their Persistence**: Models handle serialization/deserialization
- **Services Have No Presentation**: Services return simple types or raise exceptions
- **Validators at Parameter Level**: Input validation via Typer callbacks
- **Decorators for Cross-Cutting**: Error handling and auto-save via decorators
- **Testability First**: Everything can be tested in isolation with mocks

### Testing Strategy
- **One test file per module** for models and services
- **All commands tested** in `tests/test_commands.py`
- **AAA pattern**: Arrange-Act-Assert
- **Pytest fixtures**: For common setup (address book, sample contacts)
- **Comprehensive coverage**: Models, services, commands, utilities, container
- **Mock external dependencies**: Use mocks for isolation

### Adding New Code
1. **Write the code** following MVCS pattern
2. **Add type hints** to all functions and methods
3. **Write docstrings** with Args, Returns, Raises sections
4. **Write tests** in appropriate test file
5. **Run tests** with `pytest` to ensure all pass
6. **Check coverage** with `pytest --cov=src`
7. **Update README** if adding new features

### Code Review Checklist
- [ ] Type hints on all functions/methods?
- [ ] Docstrings with Args/Returns/Raises?
- [ ] Tests written and passing?
- [ ] Commands use `@handle_service_errors` decorator?
- [ ] UPDATE commands use `@auto_save` decorator?
- [ ] Parameter validation via Typer callbacks?
- [ ] Business logic in services (not commands)?
- [ ] No presentation logic in services?
- [ ] README updated if needed?

## License

This project is open source and available for educational purposes.

## Contributing

Contributions are welcome! Please follow these guidelines:

### Before Submitting
1. **Run all tests**: `pytest` - All tests must pass
2. **Check coverage**: `pytest --cov=src` - Maintain high coverage
3. **Follow code standards**: Type hints, docstrings, PEP 8
4. **Use MVCS pattern**: Keep layers separated
5. **Update documentation**: Update README for new features

### Pull Request Process
1. Create a feature branch from `main`
2. Write code following project standards
3. Add comprehensive tests for new code
4. Update README.md if adding features
5. Ensure all tests pass and coverage is maintained
6. Submit PR with clear description of changes
