#!/usr/bin/env python3
"""
Setup and Verification Script

Verifies that the Portainer API client is properly configured and can connect
to the Portainer server.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add Scripts to path
scripts_dir = Path(__file__).parent / "Scripts"
sys.path.insert(0, str(scripts_dir))

# Load environment variables from .env if present
project_root = Path(__file__).parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
    print_info(f"Loaded environment variables from {env_file}")

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(text):
    """Print a formatted header."""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")


def print_success(text):
    """Print success message."""
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    """Print error message."""
    print(f"{RED}✗ {text}{RESET}")


def print_warning(text):
    """Print warning message."""
    print(f"{YELLOW}⚠ {text}{RESET}")


def print_info(text):
    """Print info message."""
    print(f"{BLUE}ℹ {text}{RESET}")


def check_environment():
    """Check Python environment."""
    print_header("Environment Check")
    
    # Check Python version
    if sys.version_info >= (3, 11):
        print_success(f"Python {sys.version.split()[0]} (required: 3.11+)")
    else:
        print_error(f"Python {sys.version.split()[0]} (required: 3.11+)")
        return False
    
    return True


def check_dependencies():
    """Check if required packages are installed."""
    print_header("Dependencies Check")
    
    required_packages = {
        "requests": "HTTP client library",
        "yaml": "YAML configuration parser",
    }
    
    all_ok = True
    for package, description in required_packages.items():
        try:
            __import__(package)
            print_success(f"{package}: {description}")
        except ImportError:
            print_error(f"{package}: {description} (NOT INSTALLED)")
            all_ok = False
    
    if not all_ok:
        print_warning("\nInstall missing packages with:")
        print(f"  pip install -r requirements.txt")
    
    return all_ok


def check_configuration():
    """Check configuration files."""
    print_header("Configuration Check")
    
    config_file = Path(__file__).parent / "config" / "portainer.yaml"
    
    if not config_file.exists():
        print_error(f"Configuration file not found: {config_file}")
        return False
    
    print_success(f"Configuration file found: {config_file}")
    
    # Try loading configuration
    try:
        from config import create_config_manager
        config_mgr = create_config_manager()
        portainer_config = config_mgr.get_portainer_config()
        
        # Extract and display configuration
        server_url = portainer_config.get("server", {}).get("url", "NOT SET")
        username = portainer_config.get("auth", {}).get("username", "NOT SET")
        verify_ssl = portainer_config.get("server", {}).get("verify_ssl", True)
        
        print_info(f"Server URL: {server_url}")
        print_info(f"Username: {username}")
        print_info(f"Verify SSL: {verify_ssl}")
        
        if username == "your-password-here" :
            print_warning("\nConfiguration needs to be updated:")
            print_warning("  1. Set server.url in config/portainer.yaml")
            print_warning("  2. Set auth.username and auth.password")
            return False
        
        return True
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        return False


def check_connectivity():
    """Check connectivity to Portainer server."""
    print_header("Connectivity Check")
    
    try:
        from config import create_config_manager
        from portainer_client import PortainerClient, PortainerAuthError
        
        config_mgr = create_config_manager()
        portainer_config = config_mgr.get_portainer_config()
        
        server_url = portainer_config["server"]["url"]
        print_info(f"Attempting to connect to: {server_url}")
        
        client = PortainerClient(
            url=server_url,
            username=portainer_config["auth"]["username"],
            password=portainer_config["auth"]["password"],
            verify_ssl=portainer_config["server"].get("verify_ssl", True),
            timeout=10,
        )
        
        # Try to authenticate
        print_info("Authenticating...")
        client._authenticate()
        print_success("Authentication successful!")
        
        # Try to get stacks
        print_info("Retrieving stacks...")
        stacks = client.get_stacks()
        print_success(f"Retrieved {len(stacks)} stacks")
        
        return True
    except PortainerAuthError as e:
        print_error(f"Authentication failed: {e}")
        return False
    except Exception as e:
        print_error(f"Connection failed: {e}")
        return False


def show_next_steps():
    """Show next steps for user."""
    print_header("Next Steps")
    
    print("You can now use the Portainer CLI with the following commands:\n")
    
    print(f"{YELLOW}List all stacks:{RESET}")
    print("  python Scripts/main.py list\n")
    
    print(f"{YELLOW}Start a stack:{RESET}")
    print("  python Scripts/main.py start --id 1")
    print("  python Scripts/main.py start --name my-stack\n")
    
    print(f"{YELLOW}Stop a stack:{RESET}")
    print("  python Scripts/main.py stop --id 1")
    print("  python Scripts/main.py stop --name my-stack\n")
    
    print(f"{YELLOW}Get stack details:{RESET}")
    print("  python Scripts/main.py inspect --id 1\n")
    
    print(f"{YELLOW}View help:{RESET}")
    print("  python Scripts/main.py --help\n")
    
    print(f"{YELLOW}Run examples:{RESET}")
    print("  python example.py\n")


def main():
    """Run all checks."""
    print(f"\n{BLUE}Portainer API Setup Verification{RESET}")
    
    checks = [
        ("Environment", check_environment),
        ("Dependencies", check_dependencies),
        ("Configuration", check_configuration),
        ("Connectivity", check_connectivity),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"{name} check failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Verification Summary")
    
    all_passed = True
    for name, result in results:
        if result:
            print_success(f"{name}")
        else:
            print_error(f"{name}")
            all_passed = False
    
    if all_passed:
        print(f"\n{GREEN}All checks passed!{RESET}")
        show_next_steps()
        return 0
    else:
        print(f"\n{RED}Some checks failed. Please fix the issues above.{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
