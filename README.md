# Portainer API

A Python-based API client for Portainer with support for stack management operations.

## Features

- **Authentication**: Secure login to Portainer servers using username/password
- **Stack Management**: List, start, stop, and inspect Docker stacks
- **Configuration**: YAML-based configuration with environment variable support
- **CLI Interface**: Command-line tool for quick operations
- **Python API**: Programmatic access to Portainer operations

## Quick Start

### Prerequisites

- Python 3.11+
- Access to a Portainer server (CE)
- Network connectivity to Portainer server

### Setup

```bash
# Clone or create the project
cd portainer_api

# Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Edit `config/portainer.yaml` with your Portainer server details:

```yaml
server:
  url: "https://portainer.example.com"
  verify_ssl: true          # Set to false for self-signed certificates
  default_endpoint_id: 1    # Docker environment ID

auth:
  username: "admin"
  password: "your-password"  # Or use environment variable: ${PORTAINER_PASSWORD}
```

### Usage

#### CLI Commands

**List all stacks:**
```bash
python Scripts/main.py list
```

**Start a stack:**
```bash
# By ID
python Scripts/main.py start --id 1

# By name
python Scripts/main.py start --name my-stack
```

**Stop a stack:**
```bash
# By ID
python Scripts/main.py stop --id 1

# By name
python Scripts/main.py stop --name my-stack
```

**Get stack details:**
```bash
python Scripts/main.py inspect --id 1
```

**List stacks on specific endpoint:**
```bash
python Scripts/main.py list --endpoint-id 1
```

**Verbose output:**
```bash
python Scripts/main.py -v list
```

#### Python API

```python
from Scripts.config import create_config_manager
from Scripts.portainer_client import PortainerClient
from Scripts.stack_manager import StackManager

# Load configuration
config_mgr = create_config_manager()
portainer_config = config_mgr.get_portainer_config()

# Initialize client
client = PortainerClient(
    url=portainer_config["server"]["url"],
    username=portainer_config["auth"]["username"],
    password=portainer_config["auth"]["password"],
    verify_ssl=portainer_config["server"].get("verify_ssl", True),
)

# Create manager
manager = StackManager(client)

# List stacks
stacks = manager.list_stacks()
for stack in stacks:
    print(f"{stack.name}: {stack.status_name}")

# Start a stack
stack = manager.start_stack(stack_id=1)

# Stop a stack
stack = manager.stop_stack(stack_id=1)

# Find stack by name
stack = manager.get_stack_by_name("my-stack")
```

## Project Structure

```
portainer_api/
├── Scripts/
│   ├── main.py              # Entry point
│   ├── cli.py               # CLI interface
│   ├── config.py            # Configuration management
│   ├── portainer_client.py   # Portainer API client
│   ├── stack_manager.py      # Stack operations
│   └── __init__.py
├── config/
│   ├── portainer.yaml       # Portainer server config
├── example.py               # Usage examples
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── .github/
    └── copilot-instructions.md  # Development guidelines
```

## Configuration Details

### portainer.yaml

| Setting | Description | Example |
|---------|-------------|---------|
| `server.url` | Portainer server URL | `https://portainer.example.com` |
| `server.verify_ssl` | Verify SSL certificates | `true` or `false` |
| `server.default_endpoint_id` | Default Docker environment ID | `1` |
| `auth.username` | Portainer username | `admin` |
| `auth.password` | Portainer password or env var | `password` or `${PORTAINER_PASSWORD}` |
| `request_timeout` | API request timeout (seconds) | `30` |

### Environment Variables

You can use environment variables in configuration:

```yaml
auth:
  password: "${PORTAINER_PASSWORD}"
```

Then set the environment variable:
```bash
export PORTAINER_PASSWORD="your-password"
```

## Supported Operations

### Stack Operations

| Operation | Command | API Endpoint |
|-----------|---------|-----------|
| List stacks | `list` | GET `/stacks` |
| Get stack | `inspect --id <id>` | GET `/stacks/{id}` |
| Start stack | `start --id <id>` | POST `/stacks/{id}/start` |
| Stop stack | `stop --id <id>` | POST `/stacks/{id}/stop` |

### Stack Status

- `1` or "Running" - Stack is active
- `2` or "Stopped" - Stack is stopped

## Examples

See `example.py` for comprehensive usage examples:

```bash
python example.py
```

## Error Handling

The client includes error handling for:

- **PortainerAuthError**: Authentication failures (invalid credentials)
- **PortainerAPIError**: API communication errors
- **StackManagerError**: Stack operation failures
- **ConfigError**: Configuration loading issues

## Security Considerations

1. **Never hardcode passwords** - Use environment variables
2. **Use HTTPS** - Set `verify_ssl: true` in production
3. **Restrict file permissions** - Protect `config/portainer.yaml`
4. **Use strong passwords** - Portainer credentials should be secure
5. **Rotate tokens** - JWT tokens are cached; implement rotation as needed

## API Documentation

For complete Portainer API documentation, see:
https://api-docs.portainer.io/?edition=ce&version=2.39.0

## Development

### Code Style

```bash
# Format code
black Scripts/

# Lint code
flake8 Scripts/

# Type checking
mypy Scripts/
```

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=Scripts
```

### Adding New Operations

To add new stack operations:

1. Add method to `PortainerClient` in `portainer_client.py`
2. Create wrapper method in `StackManager` in `stack_manager.py`
3. Add CLI command in `cli.py`
4. Update documentation

## License

Add your license information here.

## Contributing

Guidelines for contributing to this project.

