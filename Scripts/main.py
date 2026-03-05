"""
Portainer API - Main Entry Point

Entry point for running the Portainer stack management CLI.
Supports commands: list, start, stop, inspect
"""

import sys
from pathlib import Path

# Add Scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from cli import main as cli_main


def main() -> None:
    """Main application entrypoint."""
    # Run CLI
    exit_code = cli_main(sys.argv[1:])
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
