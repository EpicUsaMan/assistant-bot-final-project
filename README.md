# Assistant Bot - Modern Contact Manager

![Coverage](./coverage.svg)

A professional console-based contact management system built with **MVCS architecture**, **Dependency Injection**, and **modern Python best practices**. Features interactive REPL mode, beautiful terminal UI, comprehensive validation, and automatic data persistence.

**Tech Stack:** Python 3.10+ • Typer • Rich • Click-REPL • Dependency Injector • Pytest

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Features](#features)
- [Available Commands](#available-commands)
- [Architecture](#architecture)
- [Testing](#testing)
- [Development](#development)
- [Contributing](#contributing)

## Python Version

Python 3.10 or higher required

## Installation

```bash
pip install -r requirements.txt
```

### Shell Completion (Optional)

Enable TAB autocomplete for contact names, note names, and subcommands:

```bash
# Bash - add to ~/.bashrc
eval "$(_ASSISTANT_BOT_COMPLETE=bash_source python src/main.py)"

# Zsh - add to ~/.zshrc
eval "$(_ASSISTANT_BOT_COMPLETE=zsh_source python src/main.py)"

# Then reload your shell
source ~/.bashrc  # or ~/.zshrc
```

## Dependencies
- **typer** (>=0.12) - Modern CLI framework
- **click** (>=8.1) - Command-line interface creation kit
- **click-repl** (>=0.3) - REPL plugin for Click
- **rich** (>=13.7) - Beautiful terminal formatting
- **dependency-injector** (>=4.41) - Dependency injection framework
- **phonenumbers** (>=8.13) - International phone number parsing and formatting
- **pytest** (>=8.0.0) - Testing framework
- **pytest-cov** (>=4.0.0) - Test coverage plugin
- **coverage-badge** (>=1.1.0) - Generate coverage badges

## Quick Start

### Interactive Mode (REPL)

```bash
# Start interactive mode
python src/main.py

# Work with contacts
> add John 1234567890
> add-birthday John 15.05.1990
> email add John john@example.com
> address set John UA Kyiv "Main St 1"
> all
> birthdays

# Work with notes
> notes add John "Meeting" "Discuss Q4 targets"
> notes list John
> notes tag-add John "Meeting" important work

# Search
> search contacts "john"
> search notes "meeting"

# Exit
> exit
```

### CLI Mode

```bash
# View all commands
python src/main.py --help

# Add a contact (flexible phone formats accepted)
python src/main.py add "John Doe" 067-235-5960
python src/main.py add "John Doe" +380 67 235 5960
python src/main.py add "John Doe" 00380672355960

# Show all contacts
python src/main.py all

# Show all contacts sorted
python src/main.py all --sort-by name

# Birthday commands
python src/main.py add-birthday "John Doe" 15.05.1990
python src/main.py birthdays

# Tags
python src/main.py tag-add "John Doe" ml ai
python src/main.py all --sort-by tag_count

# Email and Address
python src/main.py email add "John Doe" "john@example.com"
python src/main.py email remove "John Doe"
python src/main.py address set "John Doe" "UA" "Kyiv" "Main St 1"
python src/main.py address remove "John Doe"

# Notes
python src/main.py notes add "John" "Meeting" "Discuss project"
python src/main.py notes tag-add "John" "Meeting" important work
python src/main.py notes list "John"

# Search
python src/main.py search contacts "john" --by=name
python src/main.py search notes "meeting" --by=text
```

## Features

### Core Functionality
- **Contact Management**: Add, edit, delete contacts with multiple phones and birthdays
- **Email Management**: Add and remove email addresses with validation and normalization
- **Address Management**: Set and remove addresses with interactive country/city selection
- **Notes System**: Text notes attached to contacts with full CRUD operations
- **Tagging**: Tag both contacts and notes for organization
- **Advanced Search**: Search by name, phone, tags, notes content with flexible criteria
- **Birthday Tracking**: Automatic upcoming birthdays with weekend adjustment

### User Experience
- **Interactive REPL mode** for conversational usage
- **CLI mode** for single-command execution and scripting
- **Interactive menus** with arrow key navigation (questionary)
- **Beautiful terminal UI** with Rich library formatting
- **TAB autocomplete** for commands, contact names, and note names

### Technical
- **MVCS Architecture** with clear separation of concerns
- **Dependency Injection** for testability and maintainability
- **Auto-registration** of commands
- **Two-tier validation** with user-friendly error messages
- **Automatic data persistence** via decorators
- **Comprehensive test coverage** with pytest

## Available Commands

### Contact Management
| Command | Arguments | Description |
|---------|-----------|-------------|
| `add` | name, phone | Add a new contact or add phone to existing contact |
| `change` | name, old_phone, new_phone | Change an existing phone number |
| `phone` | name | Show all phone numbers for a contact |
| `all` | `[--sort-by MODE]` | Show all contacts (sort by: name, phone, birthday, tag_count, tag_name) |
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
| `group-list`    | None                          | Show all groups with contact counts and current mark |
| `group-add`     | `<group_id>`                  | Create a new group                                   |
| `group-use`     | `<group_id>`                  | Switch active group                                  |

### Email Management
| Command | Arguments | Description |
|---------|-----------|-------------|
| `email add` | contact_name, email | Add or update email address for a contact |
| `email remove` | contact_name | Remove email address from a contact |
| `email` | None | Interactive email management menu |

**Email Features:**
- Automatic normalization to lowercase
- Format validation (RFC-compliant)
- Works reliably in all terminals (uses typer.prompt for @ symbol compatibility)

**Examples:**
```bash
# Interactive mode - prompts for missing parameters
> email add
> email add "John Doe"
> email add "John Doe" "john@example.com"

# Remove email
> email remove "John Doe"
```

### Address Management
| Command | Arguments | Description |
|---------|-----------|-------------|
| `address set` | contact_name, country, city, address_line | Set address for a contact with interactive selection |
| `address remove` | contact_name | Remove address from a contact |
| `address` | None | Interactive address management menu |

**Address Features:**
- Interactive country selection from predefined catalog
- Interactive city selection with option to add new cities
- Supports partial address (country only, country+city, or full address)
- User-added cities are saved to catalog for future use

**Examples:**
```bash
# Fully interactive - prompts for all parameters
> address set

# Partially interactive - prompts for missing parameters
> address set "John Doe"
> address set "John Doe" "UA"
> address set "John Doe" "UA" "Kyiv"
> address set "John Doe" "UA" "Kyiv" "Main St 1"

# Remove address
> address remove "John Doe"
```

**Interactive Selection:**
- Country: Choose from predefined list (UA, PL, US, GB, DE, FR, IT, ES, CA, AU)
- City: Select from existing cities or add new one if not found
- Address line: Free text input

### Groups: CLI usage

Basic workflow for managing groups and grouped contacts:

```bash
# List all groups with contact counts, current group is marked
python src/main.py group-list

# Create a new group
python src/main.py group-add work

# Switch active group
python src/main.py group-use work

# Add contacts into the current group (here: work)
python src/main.py add "John Doe" 1234567890

# Switch back to personal and add another contact
python src/main.py group-use personal
python src/main.py add "Alice" 1111111111

# Show contacts only from the current group (default behaviour)
python src/main.py all

# Show contacts only from a specific group
python src/main.py all --group work

# Show contacts from all groups, grouped in output
python src/main.py all --group all
```

In interactive mode the prompt shows the current group, for example:

```text
[personal] >
[work] >
```


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
Phone number field with international parsing and formatting (inherits from Field).

**Attributes:**
- `value: str` - Canonical E.164 format (e.g., `+380672355960`)
- `country_code: int` - Country code (e.g., `380` for Ukraine)
- `national_number: int` - National number without country code
- `display_value: str` - Human-readable international format (e.g., `+380 67 235 5960`)
- `display_value_national: str` - National format (e.g., `067 235 5960`)

**Validation:** 
- Accepts flexible input formats (with/without country code, spaces, dashes, parentheses)
- Defaults to Ukraine (+380) if no country code provided
- Uses `phonenumbers` library for parsing and validation
- Stores canonical E.164 format internally
- Displays formatted numbers in international format by default

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

## Contact Groups

The address book supports **contact groups** (for example: `personal`, `work`, `family`, `other`) to organize contacts and scope name uniqueness.

### Core ideas

- Each contact belongs to **exactly one group**.
- Default group id: **`personal`**.
- Contact names are **unique within a group**, not globally.
- Every record stores its group in `Record.group_id`.
- The address book keeps:
  - `AddressBook.groups: dict[str, Group]` – registry of known groups.
  - `AddressBook.current_group_id: str` – id of the currently active group.

### Models

- `Group` (`src/models/group.py`)
  - `id: str` – normalized group identifier (e.g. `work`, `personal`).
  - `title: str | None` – optional human‑readable title.
  - `DEFAULT_GROUP_ID = "personal"`.
  - Helper: `normalize_group_id(group_id: str) -> str`.

- `Record` (`src/models/record.py`)
  - Extra field: `group_id: str | None` – id of the group this contact belongs to.
  - `__setstate__` keeps backward compatibility:
    - Adds `tags` for old pickles that do not have it.
    - Ensures `group_id` exists (defaults to `personal` for old data).

- `AddressBook` (`src/models/address_book.py`)
  - New attributes:
    - `groups: dict[str, Group]`
    - `current_group_id: str`
  - Group API:
    - `add_group(group_id: str, title: str | None = None) -> Group`
    - `has_group(group_id: str) -> bool`
    - `iter_groups() -> Iterable[Group]`
    - `iter_group(group_id: str) -> list[tuple[str, Record]]` – contacts of a single group.
    - `iter_all() -> list[tuple[str, Record]]` – contacts from all groups.

## Utilities

### Validators (`src/utils/validators.py`)
CLI parameter validators used as Typer callbacks for input validation at the parameter level.

**Available Validators:**
- `validate_phone(value: str) -> str` - Validates and normalizes phone number (flexible input formats)
  - Accepts: local formats (e.g., `067-235-5960`), international formats (e.g., `+380 67 235 5960`), with/without country code
  - Returns: Canonical E.164 format (e.g., `+380672355960`)
  - Defaults to Ukraine (+380) if no country code provided
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

**Tag Rules:** lowercase, `[a-z0-9_-]`, length `1..32`, unique per contact

### Notes
| Command | Arguments | Description |
|---------|-----------|-------------|
| `notes add` | contact_name, note_name, content | Add a text note to a contact |
| `notes edit` | contact_name, note_name, content | Edit an existing note's content |
| `notes delete` | contact_name, note_name | Delete a note from a contact |
| `notes list` | contact_name | List all notes for a contact |
| `notes show` | contact_name, note_name | Show full content of a specific note |
| `notes tag-add` | contact_name, note_name, tags... | Add tags to a note |
| `notes tag-remove` | contact_name, note_name, tag | Remove a tag from a note |
| `notes tag-clear` | contact_name, note_name | Clear all tags from a note |
| `notes tag-list` | contact_name, note_name | List all tags for a note |
| `notes menu` | None | Interactive notes management menu |

### Search
| Command | Arguments | Description |
|---------|-----------|-------------|
| `search contacts` | query, --by=TYPE | Search for contacts across specified fields |
| `search notes` | query, --by=TYPE | Search for notes across specified fields |
| `search menu` | None | Interactive search menu |

**Search Types for Contacts:**
- `all` (default), `name`, `phone`, `tags`, `tags-all` (AND), `tags-any` (OR)
- `notes-text`, `notes-name`, `notes-tags`

**Search Types for Notes:**
- `all` (default), `name`, `text`, `tags`
- `contact-name`, `contact-phone`, `contact-tags`

### Other
| Command | Description |
|---------|-------------|
| `hello` | Get a greeting from the bot |
| `interactive` | Start interactive REPL mode |

## Architecture

This project follows the **Model-View-Controller-Service (MVCS)** architecture pattern.


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
   - Accepts flexible formats: local (e.g., `067-235-5960`), international (e.g., `+380 67 235 5960`), with spaces/dashes/parentheses
   - Automatically normalizes to E.164 format (e.g., `+380672355960`)
   - Defaults to Ukraine (+380) if no country code provided
   - Validates using `phonenumbers` library for international support
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
3. **Phone field**: Validates and normalizes phone numbers using `phonenumbers` library (defense in depth)
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

```

Or via environment variables or config files using dependency-injector's configuration system.

### Groups migration (backward compatibility)

Existing `addressbook.pkl` files created **before** groups existed are migrated automatically when loaded:

- Old records without `tags` get an empty `Tags()` instance.
- Old records without `group_id` are assigned to the default group `personal`.
- Old keys stored as just `"John"` are migrated to the new format `"personal:John"`.
- Any `group_id` found in records but missing in `AddressBook.groups` is auto‑registered as a `Group`.

This logic lives in:

- `Record.__setstate__` – adds missing `tags` / `group_id` on unpickling.
- `AddressBook.load_from_file` – creates `groups`, `current_group_id`, and rewrites keys to the `<group_id>:<name>` scheme when necessary.

No manual migration steps are required – just run the updated application and the data will be upgraded in memory before the next save.

### Phone number migration (backward compatibility)

Existing `addressbook.pkl` files created **before** flexible phone formatting was implemented are migrated automatically when loaded:

- Old phone numbers stored as 10-digit strings (e.g., `"1234567890"`) are automatically converted to the new `Phone` model with E.164 format (e.g., `+3801234567890`)
- Phone numbers are normalized and formatted during migration
- All phone operations (add, remove, edit, find) now work with flexible input formats while maintaining compatibility with old data

This logic lives in:
- `Record.__setstate__` – migrates old phone strings/objects to new `Phone` instances with proper normalization
- `Phone.__init__` – handles parsing of various input formats and defaults to Ukraine (+380) when no country code is present

No manual migration steps are required – just run the updated application and phone numbers will be upgraded automatically.


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

> add John 067-235-5960
Contact added.

> add-birthday John 15.05.1990
Birthday added.

> all
╭────────────── All Contacts ──────────────╮
│ Contact name: John, phones: +380 67 235 5960,  │
│ birthday: 15.05.1990                     │
╰──────────────────────────────────────────╯

> exit
Good bye!
```

### Command-Line Mode

```bash
# Add contacts (flexible phone formats)
python src/main.py add Alice +1 555-123-4567
python src/main.py add Bob 067-235-5960
python src/main.py add Charlie +380 50 123 4567

# Add birthdays
python src/main.py add-birthday Alice 10.03.1995
python src/main.py add-birthday Bob 25.12.1990

# View all contacts
python src/main.py all

# View upcoming birthdays
python src/main.py birthdays
```

### Key Design Principles

- **Commands ARE Controllers** - No separate controller layer needed
- **Dependency Injection** - All dependencies injected via container
- **Auto-registration** - Commands automatically discovered and registered
- **Decorators for Cross-Cutting Concerns** - Error handling (`@handle_service_errors`) and auto-save (`@auto_save`)
- **Two-tier Validation** - CLI parameter validation + model validation
- **Automatic Persistence** - Data saved automatically after UPDATE operations

### Adding New Features

#### Adding a New Command

1. Create `src/commands/my_command.py`:

```python
import typer
from dependency_injector.wiring import inject, Provide
from rich.console import Console
from src.container import Container
from src.services.contact_service import ContactService
from src.utils.command_decorators import handle_service_errors, auto_save
from src.utils.validators import validate_phone

app = typer.Typer()
console = Console()

@inject
@handle_service_errors  # Always include for error handling
@auto_save  # Include only for UPDATE commands (not READ commands)
def _my_command_impl(
    name: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    """Implementation with service logic."""
    result = service.some_method(name)
    console.print(f"[green]{result}[/green]")

@app.command(name="my-command")
def my_command(
    name: str = typer.Argument(..., help="Contact name"),
    phone: str = typer.Argument(..., callback=validate_phone),  # Optional: add validation
):
    """Command description."""
    return _my_command_impl(name)
```

2. Add to wiring in `src/main.py`:

```python
container.wire(modules=[
    # ... existing modules
    "src.commands.my_command",
])
```

3. Command is automatically registered!

#### Adding a Service Method

Add method to appropriate service in `src/services/`:

```python
def my_method(self, param: str) -> str:
    """
    Method description.
    
    Args:
        param: Parameter description
        
    Returns:
        Result description
        
    Raises:
        ValueError: If validation fails
    """
    # Business logic here
    if not param:
        raise ValueError("Parameter required")
    return f"Result: {param}"
```

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
# Generate coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Update coverage badge
coverage-badge -o coverage.svg -f
```

### Run Specific Tests

Users see which parameter failed: `Invalid value for 'PHONE': Invalid phone number: ...` or `Phone number is not possible: ...`

**2. Error Handling (Decorator)**

Catch service errors without try/except blocks:
```bash
# Test models
pytest tests/test_address_book.py
pytest tests/test_record.py
pytest tests/test_email.py
pytest tests/test_address.py

# Test services
pytest tests/test_contact_service.py

# Test commands
pytest tests/test_commands.py
pytest tests/test_email_commands.py
pytest tests/test_address_commands.py
```

### Test Organization

- **One test file per module** for models and services
- **All commands tested** in `tests/test_commands.py`
- **AAA pattern** - Arrange, Act, Assert
- **Pytest fixtures** for common setup
- **Mock dependencies** for isolation

## Development

### Code Standards

- **Type hints** on all functions and methods
- **Docstrings** with Args, Returns, Raises sections
- **English only** for all comments and documentation
- **PEP 8 compliance** - Consistent code formatting
- **Low complexity** - Simple, readable code
- **Meaningful names** - Clear, descriptive naming

### MVCS Anti-patterns to Avoid

- Business logic in Commands (delegate to services)
- Presentation logic in Services (use Rich in commands only)
- Models calling Services
- Commands calling other Commands directly
- Fat commands (move logic to services)

### Command Checklist

- [ ] Parameters validated with `@typer.Argument(..., callback=validate_*)`?
- [ ] `@handle_service_errors` decorator present?
- [ ] UPDATE commands have `@auto_save`?
- [ ] READ commands do NOT have `@auto_save`?
- [ ] Decorator order: `@inject` → `@handle_service_errors` → `@auto_save`?
- [ ] Business logic in service (not command)?
- [ ] Presentation logic in command (not service)?

## Data Validation

### Two-Tier Validation

1. **CLI Parameter Validation** (Typer callbacks):
   - Phone: exactly 10 digits
   - Birthday: DD.MM.YYYY format
   - Email: RFC-compliant format, normalized to lowercase
   - Tags: `[a-z0-9_-]`, length `1..32`
   - User sees which parameter failed

2. **Model Validation** (defense in depth):
   - Additional validation in model constructors
   - Prevents invalid data at data layer
   - Raises exceptions caught by `@handle_service_errors`

## Data Persistence

- **Loading**: Address book loaded on startup from `addressbook.pkl`
- **Saving**: Automatic via `@auto_save` decorator on UPDATE commands
- **Format**: Python pickle (binary)
- **Location**: Configurable in DI container (default: `addressbook.pkl`)

## Dependencies

- **typer** (>=0.12) - Modern CLI framework
- **click** (>=8.1) - Command-line interface kit
- **click-repl** (>=0.3) - REPL plugin for Click
- **rich** (>=13.7) - Beautiful terminal formatting
- **dependency-injector** (>=4.41) - DI framework
- **questionary** (>=2.0.0) - Interactive prompts
- **pytest** (>=8.0.0) - Testing framework
- **pytest-cov** (>=4.0.0) - Test coverage
- **coverage-badge** (>=1.1.0) - Coverage badges

## Contributing

Contributions welcome! Please follow these guidelines:

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

## License

This project is open source and available for educational purposes.
