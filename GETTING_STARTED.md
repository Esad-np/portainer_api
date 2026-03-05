# Getting Started with Portainer API Client

A comprehensive guide to setting up and using the Portainer stack management API.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Verification](#verification)
5. [Usage](#usage)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

- **Python 3.11 or higher** - Check with `python3 --version`
- **Portainer Server** - Community Edition (CE) v2.39.0 or compatible
- **Network Access** - Can reach your Portainer server
- **Credentials** - Portainer username and password with stack management permissions

## Installation

### Step 1: Clone/Download the Project

```bash
cd portainer_api
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

The `requirements.txt` includes:
- **requests**: HTTP client for API calls
- **pyyaml**: Configuration file parsing
- **pydantic**: Data validation
- **pytest**: Testing framework

## Configuration

### Step 1: Locate Configuration File

```
config/portainer.yaml
```

### Step 2: Update Server Details

Open `config/portainer.yaml` and update:

```yaml
server:
  # Replace with your Portainer server URL
  url: "https://portainer.eb-roonserver.duckdns.org"
  
  # Set to false if using self-signed SSL certificate
  verify_ssl: false
  
  # Your Docker environment/endpoint ID (usually 1 for first environment)
  default_endpoint_id: 1

auth:
  # Your Portainer username
  username: "admin"
  
  # Your Portainer password
  # Option 1: Set password directly (not recommended)
  password: "your-secure-password"
  
  # Option 2: Use environment variable (recommended)
  # password: "${PORTAINER_PASSWORD}"
```

### Step 3: Set Credentials (Optional but Recommended)

Instead of storing passwords in the config file, use environment variables:

```bash
# Linux/macOS
export PORTAINER_PASSWORD="your-secure-password"

# Windows (PowerShell)
$env:PORTAINER_PASSWORD = "your-secure-password"

# Windows (Command Prompt)
set PORTAINER_PASSWORD=your-secure-password
```

Then use in config:
```yaml
auth:
  username: "admin"
  password: "${PORTAINER_PASSWORD}"
```

## Verification

Run the verification script to ensure everything is set up correctly:

```bash
python verify_setup.py
```

Expected output:
```
============================================================
                 Environment Check
============================================================

✓ Python 3.11.x (required: 3.11+)

============================================================
              Dependencies Check
============================================================

✓ requests: HTTP client library
✓ yaml: YAML configuration parser

============================================================
              Configuration Check
============================================================

✓ Configuration file found: .../config/portainer.yaml
ℹ Server URL: https://portainer.eb-roonserver.duckdns.org
ℹ Username: admin
ℹ Verify SSL: false

============================================================
              Connectivity Check
============================================================

ℹ Attempting to connect to: https://portainer.eb-roonserver.duckdns.org
ℹ Authenticating...
✓ Authentication successful!
ℹ Retrieving stacks...
✓ Retrieved 3 stacks

============================================================
              Verification Summary
============================================================

✓ Environment
✓ Dependencies
✓ Configuration
✓ Connectivity

All checks passed!
```

If any check fails, follow the instructions provided.

## Usage

### CLI Interface

The simplest way to interact with Portainer:

```bash
python Scripts/main.py <command> [options]
```

### Available Commands

#### List Stacks

```bash
# List all stacks
python Scripts/main.py list

# Filter by endpoint ID
python Scripts/main.py list --endpoint-id 2

# Verbose output
python Scripts/main.py -v list
```

#### Start a Stack

```bash
# Start by ID
python Scripts/main.py start --id 1

# Start by name
python Scripts/main.py start --name my-app

# Start on specific endpoint
python Scripts/main.py start --id 1 --endpoint-id 2
```

#### Stop a Stack

```bash
# Stop by ID
python Scripts/main.py stop --id 1

# Stop by name
python Scripts/main.py stop --name my-app

# Stop on specific endpoint
python Scripts/main.py stop --id 1 --endpoint-id 2
```

#### Inspect Stack Details

```bash
# Get details by ID
python Scripts/main.py inspect --id 1

# Get details by name
python Scripts/main.py inspect --name my-app
```

#### Help

```bash
# Show all commands
python Scripts/main.py --help

# Show command-specific help
python Scripts/main.py start --help
```

## Examples

### Example 1: List All Stacks

```bash
$ python Scripts/main.py list

All stacks:

ID     Name                       Status     Created By     
----------------------------------------------------------------------
1      nginx                      Running    admin          
2      postgres                   Stopped    admin          
3      redis                      Running    admin          
```

### Example 2: Start a Stack by Name

```bash
$ python Scripts/main.py start --name postgres

✓ Stack 'postgres' (ID: 2) started successfully
  Status: Running
```

### Example 3: Stop a Stack by ID

```bash
$ python Scripts/main.py stop --id 1

✓ Stack 'nginx' (ID: 1) stopped successfully
  Status: Stopped
```

### Example 4: Get Stack Details

```bash
$ python Scripts/main.py inspect --id 1

Stack Details:
  ID:          1
  Name:        nginx
  Status:      Running
  Endpoint ID: 1
  Created By:  admin
```

### Using Python API

For programmatic access, use the Python modules directly:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(".") / "Scripts"))

from config import create_config_manager
from portainer_client import PortainerClient
from stack_manager import StackManager

# Load configuration
config_mgr = create_config_manager()
portainer_config = config_mgr.get_portainer_config()

# Create client
client = PortainerClient(
    url=portainer_config["server"]["url"],
    username=portainer_config["auth"]["username"],
    password=portainer_config["auth"]["password"],
    verify_ssl=portainer_config["server"].get("verify_ssl", True),
)

# Create manager
manager = StackManager(client)

# List stacks
for stack in manager.list_stacks():
    print(f"{stack.name}: {stack.status_name}")

# Start a stack
stack = manager.start_stack(stack_id=2)
print(f"Started: {stack.name}")

# Stop a stack
stack = manager.stop_stack(stack_id=1)
print(f"Stopped: {stack.name}")

# Find by name
stack = manager.get_stack_by_name("postgres")
if stack:
    print(f"Found: {stack.name} (ID: {stack.id})")
```

### Run Examples

```bash
python example.py
```

This will demonstrate:
1. Listing all stacks
2. Finding a stack by name
3. Starting a stack
4. Stopping a stack

## Troubleshooting

### Authentication Error

```
Error: Authentication failed: Invalid credentials (username or password)
```

**Solution:**
- Verify username and password in `config/portainer.yaml`
- Ensure the user has permission to manage stacks
- Check Portainer is running and accessible

### Connection Error

```
Error: Connection error: Failed to establish connection
```

**Solution:**
- Verify server URL is correct
- Check network connectivity to Portainer server
- If using self-signed SSL, set `verify_ssl: false`
- Try with `--verbose` flag for more details

### Stack Not Found

```
Stack 'my-stack' not found
```

**Solution:**
- Verify stack name is correct (case-sensitive)
- Use `list` command to see available stacks
- Check endpoint ID is correct

### SSL Certificate Error

```
Error: Certificate verification failed
```

**Solution:**
```yaml
server:
  verify_ssl: false  # For self-signed certificates (development only)
```

**Note:** For production, properly install SSL certificates.

### Configuration File Not Found

```
ConfigError: Configuration file not found
```

**Solution:**
- Verify `config/portainer.yaml` exists
- Check you're in the correct directory
- Verify file permissions: `ls -la config/portainer.yaml`

### Module Import Error

```
ModuleNotFoundError: No module named 'requests'
```

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Common Operations

### Deploy Stack Monitoring Script

```bash
# Create a simple monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
while true; do
  python Scripts/main.py list
  sleep 30
done
EOF
chmod +x monitor.sh
./monitor.sh
```

### Restart Failed Stack

```bash
#!/bin/bash
STACK_NAME="my-app"
ENDPOINT_ID=1

echo "Stopping $STACK_NAME..."
python Scripts/main.py stop --name "$STACK_NAME" --endpoint-id "$ENDPOINT_ID"
sleep 5

echo "Starting $STACK_NAME..."
python Scripts/main.py start --name "$STACK_NAME" --endpoint-id "$ENDPOINT_ID"
```

### Health Check Script

```python
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(".") / "Scripts"))

from config import create_config_manager
from portainer_client import PortainerClient

config_mgr = create_config_manager()
portainer_config = config_mgr.get_portainer_config()

try:
    client = PortainerClient(
        url=portainer_config["server"]["url"],
        username=portainer_config["auth"]["username"],
        password=portainer_config["auth"]["password"],
        verify_ssl=portainer_config["server"].get("verify_ssl", True),
    )
    client._authenticate()
    print("OK: Portainer API is accessible")
    sys.exit(0)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
```

## Advanced Topics

### Environment-Specific Configurations

Create multiple configuration files:

```yaml
# config/portainer-dev.yaml
# config/portainer-prod.yaml
```

Load specific configuration:
```python
config_mgr = create_config_manager()
config = config_mgr.load("portainer-prod")
```

### Adding Custom Operations

Extend `StackManager` with custom operations:

```python
class CustomStackManager(StackManager):
    def restart_stack(self, stack_id: int, endpoint_id: int = None) -> Stack:
        """Restart a stack (stop + start)."""
        self.stop_stack(stack_id, endpoint_id)
        time.sleep(5)
        return self.start_stack(stack_id, endpoint_id)
```

## Next Steps

1. ✅ Complete installation and verification
2. 📋 List your stacks with `python Scripts/main.py list`
3. ▶️ Try starting/stopping stacks
4. 🔧 Integrate into your automation workflow
5. 📚 Explore the [Portainer API docs](https://api-docs.portainer.io/)

## Support

For issues:
1. Check the Troubleshooting section above
2. Run `verify_setup.py` to diagnose problems
3. Use `--verbose` flag for detailed output
4. Check [Portainer documentation](https://docs.portainer.io/)

## Security Best Practices

1. **Never commit config files with passwords**
   ```bash
   echo "config/portainer.yaml" >> .gitignore
   ```

2. **Use environment variables for credentials**
   ```yaml
   password: "${PORTAINER_PASSWORD}"
   ```

3. **Use strong passwords**
   - At least 12 characters
   - Mix of upper/lowercase, numbers, symbols

4. **Restrict file permissions**
   ```bash
   chmod 600 config/portainer.yaml
   ```

5. **Use HTTPS in production**
   ```yaml
   server:
     url: "https://portainer.example.com"
     verify_ssl: true
   ```

6. **Enable API authentication**
   - Use service accounts or API keys
   - Rotate credentials regularly
   - Monitor API access logs
