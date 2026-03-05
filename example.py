"""
Portainer Stack Manager - Quick Start Guide

Example usage of the Portainer stack management API.
"""

import sys
from pathlib import Path

# Add Scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "Scripts"))

from config import create_config_manager
from portainer_client import PortainerClient
from stack_manager import StackManager


def example_list_stacks():
    """Example: List all stacks."""
    print("=" * 60)
    print("Example 1: List all stacks")
    print("=" * 60)
    
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
    
    # Create manager and list stacks
    manager = StackManager(
        client,
        default_endpoint_id=portainer_config["server"].get("default_endpoint_id", 1),
    )
    
    stacks = manager.list_stacks()
    
    print(f"\nFound {len(stacks)} stacks:\n")
    for stack in stacks:
        print(f"  • {stack.name} (ID: {stack.id})")
        print(f"    Status: {stack.status_name}")
        print(f"    Created by: {stack.created_by}\n")


def example_get_stack_by_name():
    """Example: Get a specific stack by name."""
    print("\n" + "=" * 60)
    print("Example 2: Get stack by name")
    print("=" * 60)
    
    config_mgr = create_config_manager()
    portainer_config = config_mgr.get_portainer_config()
    
    client = PortainerClient(
        url=portainer_config["server"]["url"],
        username=portainer_config["auth"]["username"],
        password=portainer_config["auth"]["password"],
        verify_ssl=portainer_config["server"].get("verify_ssl", True),
    )
    
    manager = StackManager(client)
    
    # Find a stack by name (replace with actual stack name)
    stack_name = "my-app"  # Change this
    stack = manager.get_stack_by_name(stack_name)
    
    if stack:
        print(f"\nFound stack: {stack.name}")
        print(f"  ID: {stack.id}")
        print(f"  Status: {stack.status_name}")
        print(f"  Endpoint ID: {stack.endpoint_id}")
    else:
        print(f"\nStack '{stack_name}' not found")


def example_start_stack():
    """Example: Start a stopped stack."""
    print("\n" + "=" * 60)
    print("Example 3: Start a stopped stack")
    print("=" * 60)
    
    config_mgr = create_config_manager()
    portainer_config = config_mgr.get_portainer_config()
    
    client = PortainerClient(
        url=portainer_config["server"]["url"],
        username=portainer_config["auth"]["username"],
        password=portainer_config["auth"]["password"],
        verify_ssl=portainer_config["server"].get("verify_ssl", True),
    )
    
    manager = StackManager(client)
    
    # Start a stack by ID (replace with actual stack ID)
    stack_id = 1  # Change this
    endpoint_id = portainer_config["server"].get("default_endpoint_id", 1)
    
    try:
        stack = manager.start_stack(stack_id, endpoint_id)
        print(f"\n✓ Stack '{stack.name}' started successfully")
        print(f"  Status: {stack.status_name}")
    except Exception as e:
        print(f"\n✗ Failed to start stack: {e}")


def example_stop_stack():
    """Example: Stop a running stack."""
    print("\n" + "=" * 60)
    print("Example 4: Stop a running stack")
    print("=" * 60)
    
    config_mgr = create_config_manager()
    portainer_config = config_mgr.get_portainer_config()
    
    client = PortainerClient(
        url=portainer_config["server"]["url"],
        username=portainer_config["auth"]["username"],
        password=portainer_config["auth"]["password"],
        verify_ssl=portainer_config["server"].get("verify_ssl", True),
    )
    
    manager = StackManager(client)
    
    # Stop a stack by ID (replace with actual stack ID)
    stack_id = 1  # Change this
    endpoint_id = portainer_config["server"].get("default_endpoint_id", 1)
    
    try:
        stack = manager.stop_stack(stack_id, endpoint_id)
        print(f"\n✓ Stack '{stack.name}' stopped successfully")
        print(f"  Status: {stack.status_name}")
    except Exception as e:
        print(f"\n✗ Failed to stop stack: {e}")


def main():
    """Run examples."""
    try:
        # Example 1: List all stacks
        example_list_stacks()
        
        # Uncomment to run other examples:
        # example_get_stack_by_name()
        # example_start_stack()
        # example_stop_stack()
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure you have:")
        print("  1. Updated config/portainer.yaml with your server details")
        print("  2. Set your credentials (username and password)")
        print("  3. Installed required packages: pip install -r requirements.txt")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
