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

See [SHELL_COMPLETION_SETUP.md](SHELL_COMPLETION_SETUP.md) for detailed setup instructions.

## Quick Start

### Interactive Mode (REPL)

```bash
# Start interactive mode
python src/main.py

# Work with contacts
> add John 1234567890
> add-birthday John 15.05.1990
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
# Single commands
python src/main.py add "John Doe" 1234567890
python src/main.py add-birthday "John Doe" 15.05.1990
python src/main.py all --sort-by name
python src/main.py birthdays

# Tags
python src/main.py tag-add "John Doe" ml ai
python src/main.py all --sort-by tag_count

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


### Tags
| Command | Arguments | Description |
|---------|-----------|-------------|
| `tag-add` | name, tags... | Add one or more tags to a contact |
| `tag-remove` | name, tag | Remove a tag from a contact |
| `tag-list` | name | List tags of a contact |
| `tag-clear` | name | Clear all tags for a contact |

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

### Project Structure

```
src/
├── main.py                    # CLI entry point with auto-registration
├── container.py               # Dependency injection container
├── commands/                  # Command layer (Controller + View)
│   ├── add.py                 # Contact commands
│   ├── tags.py                # Tag commands
│   ├── notes.py               # Notes commands
│   ├── search.py              # Search commands
│   └── ...
├── services/                  # Service layer (Business logic)
│   ├── contact_service.py     # Contact operations
│   ├── note_service.py        # Note operations
│   └── search_service.py      # Search operations
├── models/                    # Model layer (Data structures)
│   ├── address_book.py        # Main data container
│   ├── record.py              # Contact record
│   ├── note.py                # Note model
│   ├── tags.py                # Tags value object
│   └── ...
└── utils/                     # Cross-cutting utilities
    ├── validators.py          # Input validators
    ├── command_decorators.py  # Error handling & auto-save
    ├── interactive_menu.py    # Menu helpers
    └── ...
tests/                         # Comprehensive test suite
```

### MVCS Layers

```
Command (Controller + View) → Service (Business Logic) → Model (Data)
```

1. **Model Layer** - Data structures, validation, serialization
2. **Service Layer** - Business logic, returns simple types or raises exceptions
3. **Command Layer** - Handles user input, calls services, formats output (Controller + View)

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

```bash
# Test models
pytest tests/test_address_book.py
pytest tests/test_record.py

# Test services
pytest tests/test_contact_service.py

# Test commands
pytest tests/test_commands.py
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
