"""
Command-Line Interface for Portainer Stack Management

Provides CLI commands to interact with Portainer stacks:
- list: List all stacks
- start: Start a stopped stack
- stop: Stop a running stack
- inspect: Get details about a specific stack
- backup-all: Export stack definitions to local files
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from config import create_config_manager, ConfigError
from portainer_client import PortainerClient, PortainerAuthError, PortainerAPIError
from stack_backup import StackBackupError, export_all_stacks
from stack_manager import StackManager, StackManagerError


def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def load_project_env() -> None:
    """Load project-local environment variables when a .env file exists."""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)


def print_stacks_table(stacks: list) -> None:
    """Print stacks in a formatted table."""
    if not stacks:
        print("No stacks found.")
        return
    
    # Print header
    print(f"\n{'ID':<6} {'Name':<30} {'Status':<10} {'Created By':<15}")
    print("-" * 65)
    
    # Print data rows
    for stack in stacks:
        print(f"{stack.id:<6} {stack.name:<30} {stack.status_name:<10} {stack.created_by:<15}")
    
    print()


def cmd_list(args) -> int:
    """List all stacks."""
    try:
        config_mgr = create_config_manager()
        portainer_config = config_mgr.get_portainer_config()
        
        # Initialize client
        client = PortainerClient(
            url=portainer_config["server"]["url"],
            username=portainer_config["auth"]["username"],
            password=portainer_config["auth"]["password"],
            verify_ssl=portainer_config["server"].get("verify_ssl", True),
            timeout=portainer_config.get("request_timeout", 30),
        )
        
        # Create manager and list stacks
        manager = StackManager(
            client,
            default_endpoint_id=portainer_config["server"].get("default_endpoint_id", 1),
        )
        
        stacks = manager.list_stacks()
        
        if args.endpoint_id:
            stacks = [s for s in stacks if s.endpoint_id == args.endpoint_id]
            print(f"Stacks on endpoint {args.endpoint_id}:")
        else:
            print("All stacks:")
        
        print_stacks_table(stacks)
        return 0
        
    except ConfigError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    except PortainerAuthError as e:
        print(f"Authentication error: {e}", file=sys.stderr)
        return 1
    except PortainerAPIError as e:
        print(f"API error: {e}", file=sys.stderr)
        return 1
    except StackManagerError as e:
        print(f"Stack manager error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_start(args) -> int:
    """Start a stack by ID or name."""
    if not args.stack and not args.name:
        print("Error: Provide either --id or --name", file=sys.stderr)
        return 1
    
    try:
        config_mgr = create_config_manager()
        portainer_config = config_mgr.get_portainer_config()
        
        client = PortainerClient(
            url=portainer_config["server"]["url"],
            username=portainer_config["auth"]["username"],
            password=portainer_config["auth"]["password"],
            verify_ssl=portainer_config["server"].get("verify_ssl", True),
            timeout=portainer_config.get("request_timeout", 30),
        )
        
        manager = StackManager(
            client,
            default_endpoint_id=portainer_config["server"].get("default_endpoint_id", 1),
        )
        
        endpoint_id = args.endpoint_id or portainer_config["server"].get("default_endpoint_id", 1)
        
        # Resolve stack ID from name if needed
        stack_id = args.stack
        if args.name:
            stack = manager.get_stack_by_name(args.name)
            if not stack:
                print(f"Stack '{args.name}' not found", file=sys.stderr)
                return 1
            stack_id = stack.id
        
        # Start the stack
        stack = manager.start_stack(stack_id, endpoint_id)
        print(f"✓ Stack '{stack.name}' (ID: {stack.id}) started successfully")
        print(f"  Status: {stack.status_name}")
        return 0
        
    except ConfigError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    except PortainerAuthError as e:
        print(f"Authentication error: {e}", file=sys.stderr)
        return 1
    except StackManagerError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_stop(args) -> int:
    """Stop a stack by ID or name."""
    if not args.stack and not args.name:
        print("Error: Provide either --id or --name", file=sys.stderr)
        return 1
    
    try:
        config_mgr = create_config_manager()
        portainer_config = config_mgr.get_portainer_config()
        
        client = PortainerClient(
            url=portainer_config["server"]["url"],
            username=portainer_config["auth"]["username"],
            password=portainer_config["auth"]["password"],
            verify_ssl=portainer_config["server"].get("verify_ssl", True),
            timeout=portainer_config.get("request_timeout", 30),
        )
        
        manager = StackManager(
            client,
            default_endpoint_id=portainer_config["server"].get("default_endpoint_id", 1),
        )
        
        endpoint_id = args.endpoint_id or portainer_config["server"].get("default_endpoint_id", 1)
        
        # Resolve stack ID from name if needed
        stack_id = args.stack
        if args.name:
            stack = manager.get_stack_by_name(args.name)
            if not stack:
                print(f"Stack '{args.name}' not found", file=sys.stderr)
                return 1
            stack_id = stack.id
        
        # Stop the stack
        stack = manager.stop_stack(stack_id, endpoint_id)
        print(f"✓ Stack '{stack.name}' (ID: {stack.id}) stopped successfully")
        print(f"  Status: {stack.status_name}")
        return 0
        
    except ConfigError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    except PortainerAuthError as e:
        print(f"Authentication error: {e}", file=sys.stderr)
        return 1
    except StackManagerError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_inspect(args) -> int:
    """Inspect a specific stack."""
    if not args.stack and not args.name:
        print("Error: Provide either --id or --name", file=sys.stderr)
        return 1
    
    try:
        config_mgr = create_config_manager()
        portainer_config = config_mgr.get_portainer_config()
        
        client = PortainerClient(
            url=portainer_config["server"]["url"],
            username=portainer_config["auth"]["username"],
            password=portainer_config["auth"]["password"],
            verify_ssl=portainer_config["server"].get("verify_ssl", True),
            timeout=portainer_config.get("request_timeout", 30),
        )
        
        manager = StackManager(
            client,
            default_endpoint_id=portainer_config["server"].get("default_endpoint_id", 1),
        )
        
        # Resolve stack ID from name if needed
        stack_id = args.stack
        if args.name:
            stack = manager.get_stack_by_name(args.name)
            if not stack:
                print(f"Stack '{args.name}' not found", file=sys.stderr)
                return 1
            stack_id = stack.id
        
        # Get stack details
        stack = manager.get_stack(stack_id)
        
        print("\nStack Details:")
        print(f"  ID:          {stack.id}")
        print(f"  Name:        {stack.name}")
        print(f"  Status:      {stack.status_name}")
        print(f"  Endpoint ID: {stack.endpoint_id}")
        print(f"  Created By:  {stack.created_by}")
        print()
        
        return 0
        
    except ConfigError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    except PortainerAuthError as e:
        print(f"Authentication error: {e}", file=sys.stderr)
        return 1
    except StackManagerError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_backup(args) -> int:
    """Export all supported stack definitions to local backup files."""
    try:
        output_dir = Path(args.output_dir).expanduser() if args.output_dir else None
        manifest = export_all_stacks(output_dir)

        print(f"Backed up {manifest['exported_count']} stack(s) to {manifest['output_dir']}")
        if manifest["skipped"]:
            print(f"Skipped {manifest['skipped_count']} unsupported stack(s):")
            for skipped in manifest["skipped"]:
                print(f"  - {skipped['name']} (ID: {skipped['id']}): {skipped['reason']}")

        if manifest["failed"]:
            print(f"Failed to export {manifest['failed_count']} stack(s):", file=sys.stderr)
            for failed in manifest["failed"]:
                print(f"  - {failed['name']} (ID: {failed['id']}): {failed['reason']}", file=sys.stderr)
            return 1

        return 0

    except ConfigError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    except PortainerAuthError as e:
        print(f"Authentication error: {e}", file=sys.stderr)
        return 1
    except (PortainerAPIError, StackBackupError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main(argv: Optional[list] = None) -> int:
    """
    Main CLI entry point.
    
    Args:
        argv: Command-line arguments (uses sys.argv if None)
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="Portainer Stack Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all stacks
  %(prog)s list
  
  # Start a stack by ID
  %(prog)s start --id 1
  
  # Stop a stack by name
  %(prog)s stop --name my-stack
  
  # Get details about a stack
  %(prog)s inspect --id 1

  # Export all supported stack definitions
  %(prog)s backup-all --output-dir ./backups/portainer
        """,
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all stacks")
    list_parser.add_argument(
        "--endpoint-id",
        type=int,
        help="Filter by endpoint/environment ID"
    )
    list_parser.set_defaults(func=cmd_list)
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start a stack")
    start_parser.add_argument(
        "--id",
        type=int,
        dest="stack",
        help="Stack ID"
    )
    start_parser.add_argument(
        "--name",
        help="Stack name"
    )
    start_parser.add_argument(
        "--endpoint-id",
        type=int,
        help="Endpoint/environment ID (overrides default)"
    )
    start_parser.set_defaults(func=cmd_start)
    
    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop a stack")
    stop_parser.add_argument(
        "--id",
        type=int,
        dest="stack",
        help="Stack ID"
    )
    stop_parser.add_argument(
        "--name",
        help="Stack name"
    )
    stop_parser.add_argument(
        "--endpoint-id",
        type=int,
        help="Endpoint/environment ID (overrides default)"
    )
    stop_parser.set_defaults(func=cmd_stop)
    
    # Inspect command
    inspect_parser = subparsers.add_parser("inspect", help="Inspect a stack")
    inspect_parser.add_argument(
        "--id",
        type=int,
        dest="stack",
        help="Stack ID"
    )
    inspect_parser.add_argument(
        "--name",
        help="Stack name"
    )
    inspect_parser.set_defaults(func=cmd_inspect)

    # Backup command
    backup_parser = subparsers.add_parser(
        "backup-all",
        help="Export all supported stack definitions to local files"
    )
    backup_parser.add_argument(
        "--output-dir",
        help="Directory to write this backup run into"
    )
    backup_parser.set_defaults(func=cmd_backup)

    args = parser.parse_args(argv)
    load_project_env()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)
    
    # Execute command
    if hasattr(args, "func"):
        return args.func(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
