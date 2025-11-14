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

```bash
python src/main.py

> add John 1234567890
> add-birthday John 15.05.1990
> email add John john@example.com
> address set John UA Kyiv "Main St 1"
> notes add John "Meeting" "Discuss Q4 targets"
> all
> exit
```

### CLI Mode

```bash
python src/main.py add "John Doe" 1234567890
python src/main.py add-birthday "John Doe" 15.05.1990
python src/main.py all --sort-by name

# Birthday commands
python src/main.py add-birthday "John Doe" 15.05.1990
python src/main.py birthdays
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
| `add` | name, phone | Add a new contact or add phone to existing contact |
| `change` | name, old_phone, new_phone | Change an existing phone number |
| `phone` | name | Show all phone numbers for a contact |
| `all` | `[--sort-by MODE]` | Show all contacts (sort by: name, phone, birthday, tag_count, tag_name) |
| `add-birthday` | name, birthday (DD.MM.YYYY) | Add a birthday date to a contact |
| `show-birthday` | name | Show the birthday date for a contact |
| `birthdays` | None | Show all upcoming birthdays for the next week |
| `tag-add` | name, tag | Add a tag to a contact |
| `tag-remove` | name, tag | Remove a tag from a contact |
| `tag-list` | name | List tags of a contact |
| `tag-clear` | name | Clear all tags for a contact |
| `find-by-tags` | "t1,t2" | Find contacts that have **ALL** tags (AND) |
| `find-by-tags-any` | "t1,t2" | Find contacts that have **ANY** tag (OR) |
| `group-list` | None | Show all groups with contact counts |
| `group-add` | `<group_id>` | Create a new group |
| `group-use` | `<group_id>` | Switch active group |

### Email & Address
| Command | Arguments | Description |
|---------|-----------|-------------|
| `email add` | contact_name, email | Add or update email address |
| `email remove` | contact_name | Remove email address |
| `address set` | contact_name, country, city, address_line | Set address with interactive selection |
| `address remove` | contact_name | Remove address |

### Notes
| Command | Arguments | Description |
|---------|-----------|-------------|
| `notes add` | contact_name, note_name, content | Add a text note |
| `notes edit` | contact_name, note_name, content | Edit a note |
| `notes delete` | contact_name, note_name | Delete a note |
| `notes list` | contact_name | List all notes for a contact |
| `notes show` | contact_name, note_name | Show full content of a note |
| `notes tag-add` | contact_name, note_name, tags... | Add tags to a note |
| `notes tag-remove` | contact_name, note_name, tag | Remove a tag from a note |
| `notes tag-list` | contact_name, note_name | List tags for a note |

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
