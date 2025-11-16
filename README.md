# Assistant Bot - Modern Contact Manager

![Coverage](./coverage.svg)

A professional console-based contact management system built with **MVCS architecture**, **Dependency Injection**, and **modern Python best practices**. Features interactive REPL mode, beautiful terminal UI, comprehensive validation, and automatic data persistence.

**Tech Stack:** Python 3.10+ • Typer • Rich • Click-REPL • Dependency Injector • Pytest

## Installation

```bash
pip install -r requirements.txt
```

### Shell Completion (Optional)

```bash
# Bash - add to ~/.bashrc
eval "$(_ASSISTANT_BOT_COMPLETE=bash_source python src/main.py)"

# Zsh - add to ~/.zshrc
eval "$(_ASSISTANT_BOT_COMPLETE=zsh_source python src/main.py)"
```

## Quick Start

### Interactive Mode (REPL)

Interactive mode starts automatically when you run without arguments:

```bash
python src/main.py

> contact add John 1234567890
> contact birthday add John 15.05.1990
> contact email add John john@example.com
> contact address set John UA Kyiv "Main St 1"
> notes add John "Meeting" "Discuss Q4 targets"
> contact list
> exit
```

### CLI Mode

```bash
python src/main.py contact add "John Doe" 1234567890
python src/main.py contact birthday add "John Doe" 15.05.1990
python src/main.py contact list --sort-by name

# Birthday commands
python src/main.py contact birthday add "John Doe" 15.05.1990
python src/main.py contact birthday upcoming
```

## Features

- **Contact Management**: Add, edit, delete contacts with phones, birthdays, emails, addresses
- **Notes System**: Text notes attached to contacts with full CRUD operations
- **Tagging**: Tag both contacts and notes for organization
- **Advanced Search**: Search by name, phone, tags, notes content
- **Groups**: Organize contacts into groups
- **Interactive REPL mode** with TAB autocomplete
- **Beautiful terminal UI** with Rich library
- **Automatic data persistence**

## Available Commands

### Contact Management
| Command | Arguments | Description |
|---------|-----------|-------------|
| `contact add` | name, phone | Add a new contact or add phone to existing contact |
| `contact remove` | name | Remove a contact from the address book |
| `contact show` | name | Show detailed information about a contact |
| `contact list` | `[--sort-by MODE] [--group GROUP]` | List all contacts (sort by: name, phone, birthday, tag_count, tag_name) |

#### Phone Operations
| Command | Arguments | Description |
|---------|-----------|-------------|
| `contact phone add` | name, phone | Add a phone number to a contact |
| `contact phone remove` | name, phone | Remove a phone number (must keep at least one) |
| `contact phone change` | name, old_phone, new_phone | Change an existing phone number |
| `contact phone list` | name | Show all phone numbers for a contact |

#### Birthday Operations
| Command | Arguments | Description |
|---------|-----------|-------------|
| `contact birthday add` | name, birthday (DD.MM.YYYY) | Add a birthday date to a contact |
| `contact birthday show` | name | Show the birthday date for a contact |
| `contact birthday upcoming` | None | Show all upcoming birthdays for the next week |

#### Tag Operations
| Command | Arguments | Description |
|---------|-----------|-------------|
| `contact tag add` | name, tags... | Add one or more tags to a contact |
| `contact tag remove` | name, tag | Remove a tag from a contact |
| `contact tag list` | name | List tags of a contact |
| `contact tag clear` | name | Clear all tags for a contact |

#### Email Operations
| Command | Arguments | Description |
|---------|-----------|-------------|
| `contact email add` | contact_name, email | Add or update email address |
| `contact email remove` | contact_name | Remove email address |

#### Address Operations
| Command | Arguments | Description |
|---------|-----------|-------------|
| `contact address set` | contact_name, country, city, address_line | Set address with interactive selection |
| `contact address remove` | contact_name | Remove address |

### Notes Management
| Command | Arguments | Description |
|---------|-----------|-------------|
| `notes add` | contact_name, note_name, content | Add a text note |
| `notes edit` | contact_name, note_name, content | Edit a note |
| `notes remove` | contact_name, note_name | Remove a note |
| `notes list` | contact_name | List all notes for a contact |
| `notes show` | contact_name, note_name | Show full content of a note |

#### Note Tag Operations
| Command | Arguments | Description |
|---------|-----------|-------------|
| `notes tag add` | contact_name, note_name, tags... | Add tags to a note |
| `notes tag remove` | contact_name, note_name, tag | Remove a tag from a note |
| `notes tag list` | contact_name, note_name | List tags for a note |
| `notes tag clear` | contact_name, note_name | Clear all tags from a note |

### Groups
| Command | Arguments | Description |
|---------|-----------|-------------|
| `group list` | None | Show all groups with contact counts |
| `group add` | `<group_id>` | Create a new group |
| `group use` | `<group_id>` | Switch active group |
| `group show` | `<group_id>` | Show details about a specific group |
| `group rename` | `<old_id>` `<new_id>` | Rename a group |
| `group remove` | `<group_id>` `[--force]` | Remove a group (optionally with contacts) |

### Search
| Command | Arguments | Description |
|---------|-----------|-------------|
| `search contacts` | query, --by=TYPE | Search for contacts (all, name, phone, tags, notes-text) |
| `search notes` | query, --by=TYPE | Search for notes (all, name, text, tags) |

## Architecture

**MVCS Pattern:** Command (Controller + View) → Service (Business Logic) → Model (Data)

```
src/
├── main.py                    # CLI entry point
├── container.py               # Dependency injection container
├── commands/                  # Command layer (Controller + View)
├── services/                  # Service layer (Business Logic)
├── models/                    # Model layer (Data structures)
└── utils/                     # Cross-cutting utilities
```

### Key Principles

- **Dependency Injection** - All dependencies injected via container
- **Auto-registration** - Commands automatically discovered
- **Decorators** - Error handling (`@handle_service_errors`) and auto-save (`@auto_save`)
- **Two-tier Validation** - CLI parameter validation + model validation
- **Automatic Persistence** - Data saved automatically after UPDATE operations

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific tests
pytest tests/test_contact_service.py
pytest tests/test_commands.py
```

## Development

### Code Standards

- Type hints on all functions
- Docstrings with Args, Returns, Raises
- PEP 8 compliance
- English only for comments and documentation

### MVCS Anti-patterns to Avoid

- Business logic in Commands (delegate to services)
- Presentation logic in Services (use Rich in commands only)
- Models calling Services
- Commands calling other Commands directly

### Command Checklist

- [ ] Parameters validated with `@typer.Argument(..., callback=validate_*)`?
- [ ] `@handle_service_errors` decorator present?
- [ ] UPDATE commands have `@auto_save`?
- [ ] READ commands do NOT have `@auto_save`?
- [ ] Decorator order: `@inject` → `@handle_service_errors` → `@auto_save`?

## Data Persistence

- **Loading**: Address book loaded on startup from `addressbook.pkl`
- **Saving**: Automatic via `@auto_save` decorator on UPDATE commands
- **Format**: Python pickle (binary)

## Contributing

1. Create a feature branch from `main`
2. Write code following project standards
3. Add comprehensive tests
4. Run `pytest` - All tests must pass
5. Update README.md if adding features
6. Submit PR with clear description

## License

This project is open source and available for educational purposes.
