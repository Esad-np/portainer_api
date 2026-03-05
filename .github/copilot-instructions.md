# Portainer API – Copilot Instructions

## Project Overview

A Python-based API project for Portainer. Supports multiple API types including REST and GraphQL endpoints.

**Tech Stack:** Python 3.11+, Multiple API patterns

## Project Structure

```
portainer_api/
├── Scripts/              # All Python application code
│   ├── main.py          # Entry point
│   └── ...              # Feature-specific modules
├── config/              # YAML configuration files 
├── venv/                # Python virtual environment (auto-generated)
├── .github/             # GitHub metadata (this file)
├── requirements.txt     # Python dependencies
└── README.md           # Project documentation
```

## Development Setup

### Initial Setup
1. Create Python virtual environment: `python3.11 -m venv venv`
2. Activate: `source venv/bin/activate` (macOS/Linux)
3. Install dependencies: `pip install -r requirements.txt`

### Key Directories
- **Scripts/** — All application source code (Python modules)
- **config/** — YAML configuration files (database, API settings, logging, etc.)
- **venv/** — Python virtual environment (local, not committed)

## Python Conventions

- **Version:** Python 3.11 or higher
- **Virtual Environment:** `venv/` folder at project root
- **Dependencies:** Managed via `requirements.txt`
- **Code Style:** Follow PEP 8 (use tools: black, flake8, or ruff)
- **Type Hints:** Use type annotations where practical

## Configuration

All configuration is stored in YAML files under `config/`:
- `config/database.yaml` — Database connection settings
- `config/api.yaml` — API server settings
- `config/logging.yaml` — Logging configuration
- Add new configs as needed and document them in README.md

Environment-specific configs (dev, staging, prod) can use separate files or profile-based selection.

## Common Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Run the application
python Scripts/main.py

# Run tests (when test suite exists)
pytest

# Lint/format code
black Scripts/
flake8 Scripts/
```

## API Implementation Notes

- **REST endpoints:** Implement using Flask, FastAPI, or similar framework
- **GraphQL endpoints:** If included, use graphene or similar library
- **API Documentation:** Maintain docstrings; auto-generate OpenAPI/GraphQL schema documentation
- **Error Handling:** Consistent error response format across all endpoint types

## Git & Version Control

- Branch naming: `feature/`, `bugfix/`, `hotfix/` prefixes
- Commit messages: Clear, descriptive (e.g., "Add REST endpoint for user management")
- `.github/` folder: Store issue templates, workflows, and this file

## Code Organization Tips

- Keep feature modules organized by domain (e.g., `Scripts/users/`, `Scripts/containers/`)
- Use `Scripts/__init__.py` to define public APIs
- Configuration loading should happen early in app initialization
- Separate concerns: routes, business logic, data models, utilities

## Extension Points

When you're ready to add or configure:
- **Async/concurrency patterns** → update this file with async conventions
- **Database layer** → document ORM choice and migration strategy
- **Testing** → document test structure (unit, integration, e2e)
- **Deployment** → document Docker, cloud platform, or deployment process

