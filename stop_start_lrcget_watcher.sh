#!/bin/bash
# This script sets up the environment variables for the Portainer API application.
# It reads the configuration from the .env file and exports them for use in the application.
# Load environment variables from .env file
COMMAND=$1

# make sure you are in the script directory

cd "$(dirname "$0")"


#print the command being executed   
echo "Executing command: $COMMAND"

#Print the current working directory
echo "Current working directory: $(pwd)"


if [ "$COMMAND" != "stop" ] && [ "$COMMAND" != "start" ]; then
    echo "Usage: $0 {stop|start}"
    exit 1
fi

if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo ".env file not found. Please create one with the necessary configuration."
    exit 1
fi  
# Start the application
source venv/bin/activate
python Scripts/main.py $COMMAND --name lrcget-watcher
deactivate

