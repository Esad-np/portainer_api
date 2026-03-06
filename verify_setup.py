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
import subprocess
import argparse

# Add Scripts to path
scripts_dir = Path(__file__).parent / "Scripts"
sys.path.insert(0, str(scripts_dir))

# Load environment variables from .env if present
project_root = Path(__file__).parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
    print(f"Loaded environment variables from {env_file}")

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


# Verbosity level: 0=quiet, 1=verbose, 2=debug
VERBOSE = 0


def print_debug(text, level=1):
    """Print debug text only when VERBOSE >= level."""
    if VERBOSE >= level:
        print(f"{BLUE}DBG {text}{RESET}")


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
        print_debug(f"Python full sys.version: {sys.version}")
    else:
        print_error(f"Python {sys.version.split()[0]} (required: 3.11+)")
        return False
    
    return True


def check_venv():
    """Check that the virtual environment is present and contains a working Python."""
    print_header("Virtualenv Check")

    # Determine venv path from env var or default
    venv_env = os.environ.get("PORTAINER_API_VENV")
    project_root = Path(__file__).parent

    candidates = []
    if venv_env:
        # expand ~ and handle relative paths
        venv_path = Path(os.path.expanduser(venv_env))
        if not venv_path.is_absolute():
            venv_path = (project_root / venv_path).resolve()
        # if it points to an activate script directly, use its parent
        if venv_path.is_file():
            candidates.append(venv_path)
        if (venv_path / "bin" / "activate").exists():
            candidates.append(venv_path / "bin" / "activate")
        if (venv_path / "Scripts" / "activate").exists():
            candidates.append(venv_path / "Scripts" / "activate")

    # default local venv
    candidates.append(project_root / "venv" / "bin" / "activate")
    candidates.append(project_root / "venv" / "Scripts" / "activate")

    found_activate = None
    for c in candidates:
        try:
            if Path(c).exists():
                found_activate = Path(c)
                break
        except Exception:
            continue

    if not found_activate:
        print_error("Virtualenv activate script not found. Set PORTAINER_API_VENV or create ./venv.")
        return False

    print_success(f"Found virtualenv activate script: {found_activate}")

    # determine python executable next to activate script
    activate_parent = found_activate.parent.parent if found_activate.name == "activate" else found_activate.parent
    # typical structure: <venv>/bin/activate -> python at <venv>/bin/python
    python_candidate = None
    # try bin/python
    p1 = activate_parent / "bin" / "python"
    p2 = activate_parent / "python"
    p3 = activate_parent / "Scripts" / "python.exe"
    for p in (p1, p2, p3):
        if p.exists():
            python_candidate = p
            break

    if not python_candidate:
        # try relative from activate location
        possible = found_activate.parent / "python"
        if possible.exists():
            python_candidate = possible

    if not python_candidate:
        print_warning("Could not locate a python executable inside the virtualenv; continuing but this may fail.")
        return True

    print_info(f"Using virtualenv python: {python_candidate}")

    try:
        proc = subprocess.run([str(python_candidate), "--version"], capture_output=True, text=True, timeout=5)
        version_out = proc.stdout.strip() or proc.stderr.strip()
        if proc.returncode != 0:
            print_warning(f"Virtualenv python returned non-zero exit: {version_out}")
            return True

        print_success(f"Virtualenv python reported: {version_out}")
        # basic version check (require >= 3.11)
        parts = version_out.split()
        if len(parts) >= 2:
            ver = parts[1]
            segs = ver.split('.')
            try:
                major = int(segs[0])
                minor = int(segs[1]) if len(segs) > 1 else 0
            except Exception:
                print_debug(f"Failed to parse python version string: {ver}")
                return True

            print_debug(f"Virtualenv python version parsed: {ver} (major={major}, minor={minor})")
            if major < 3 or (major == 3 and minor < 11):
                print_error(f"Virtualenv python version {ver} is too old; requires Python 3.11+")
                return False

        return True
    except Exception as e:
        print_warning(f"Failed to run virtualenv python: {e}")
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
            mod = __import__(package)
            print_success(f"{package}: {description}")
            try:
                path = getattr(mod, "__file__", None)
                if path:
                    print_debug(f"{package} module path: {path}")
            except Exception:
                pass
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
        try:
            # Mask password if present and print safe copy when verbose/debug
            safe = {}
            for k, v in portainer_config.items():
                if k == "auth" and isinstance(v, dict):
                    safe[k] = {"username": v.get("username"), "password": ("***" if v.get("password") else None)}
                else:
                    safe[k] = v
            print_debug(f"Full portainer config (masked): {safe}")
        except Exception:
            print_debug("Failed to show full portainer config")
        
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
        print_debug(f"Connectivity config keys: {list(portainer_config.keys())}")
        
        client = PortainerClient(
            url=server_url,
            username=portainer_config["auth"]["username"],
            password=portainer_config["auth"]["password"],
            verify_ssl=portainer_config["server"].get("verify_ssl", True),
            timeout=10,
        )
        
        # Try to authenticate
        print_info("Authenticating...")
        print_debug(f"Authenticating as user: {portainer_config['auth'].get('username')}")
        client._authenticate()
        print_success("Authentication successful!")
        
        # Try to get stacks
        print_info("Retrieving stacks...")
        stacks = client.get_stacks()
        print_success(f"Retrieved {len(stacks)} stacks")
        if VERBOSE >= 2:
            try:
                names = [s.get('Name') or s.get('name') or '<unknown>' for s in stacks]
            except Exception:
                names = []
            print_debug(f"Stack names: {names}")
        
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
    parser = argparse.ArgumentParser(prog="verify_setup.py", description="Portainer API setup verifier")
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output (more than verbose)')
    args = parser.parse_args()

    global VERBOSE
    if args.debug:
        VERBOSE = 2
    elif args.verbose:
        VERBOSE = 1

    print(f"\n{BLUE}Portainer API Setup Verification{RESET}")
    
    checks = [
        ("Environment", check_environment),
        ("Virtualenv", check_venv),
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
