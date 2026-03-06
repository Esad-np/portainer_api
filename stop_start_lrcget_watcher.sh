#!/bin/bash
# This script sets up the environment variables for the Portainer API application.
# It reads the configuration from the .env file and exports them for use in the application.
#!/bin/bash
# Load environment variables from .env file and accept named arguments

# make sure you are in the script directory
cd "$(dirname "$0")"

# Named variables (no default for STACK_NAME)
COMMAND=""
STACK_NAME=""
VERBOSE=0

# Simple arg parsing: --command|-c, --stack-name|-s, positional start|stop
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --command|-c)
            COMMAND="$2"
            shift 2
            ;;
        --stack-name|-s)
            STACK_NAME="$2"
            shift 2
            ;;
        --verbose|-v)
            VERBOSE=1
            shift
            ;;
        start|stop)
            # positional convenience
            if [ -z "$COMMAND" ]; then
                COMMAND="$1"
            fi
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --command start|stop --stack-name <name> [--verbose]"
            exit 1
            ;;
    esac
done

if [ -z "$COMMAND" ] || { [ "$COMMAND" != "start" ] && [ "$COMMAND" != "stop" ]; }; then
    echo "Usage: $0 --command start|stop --stack-name <name> [--verbose]"
    exit 1
fi

if [ -z "$STACK_NAME" ]; then
    echo "Error: --stack-name is required and has no default."
    echo "Usage: $0 --command start|stop --stack-name <name> [--verbose]"
    exit 1
fi

if [ -f .env ]; then
        # export variables defined in .env (ignore comments)
        export $(grep -v '^#' .env | xargs)
else
        echo ".env file not found. Please create one with the necessary configuration."
        exit 1
fi

if [ "$VERBOSE" -eq 1 ]; then
    echo "Executing command: $COMMAND"
    echo "Stack name: $STACK_NAME"
    echo "Current working directory: $(pwd)"
fi

# Determine virtualenv activate script from PORTAINER_API_VENV or default to ./venv
VENV_ACTIVATE=""
if [ -n "$PORTAINER_API_VENV" ]; then
    # If PORTAINER_API_VENV points directly to an activate script
    if [ -f "$PORTAINER_API_VENV" ]; then
        VENV_ACTIVATE="$PORTAINER_API_VENV"
    # If it points to a venv directory, look for bin/activate
    elif [ -f "$PORTAINER_API_VENV/bin/activate" ]; then
        VENV_ACTIVATE="$PORTAINER_API_VENV/bin/activate"
    else
        echo "PORTAINER_API_VENV is set but no activate script found at $PORTAINER_API_VENV or $PORTAINER_API_VENV/bin/activate"
        exit 1
    fi
else
    if [ -f "venv/bin/activate" ]; then
        VENV_ACTIVATE="venv/bin/activate"
    else
        echo "Virtualenv activate script not found. Set PORTAINER_API_VENV to your venv path or create a 'venv' directory."
        exit 1
    fi
fi

if [ "$VERBOSE" -eq 1 ]; then
    echo "Using virtualenv activate: $VENV_ACTIVATE"
fi

# Start the application
source "$VENV_ACTIVATE"
python Scripts/main.py $COMMAND --name "$STACK_NAME"
deactivate

