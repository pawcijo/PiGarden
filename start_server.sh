#!/bin/bash

# Create a logs directory if it doesn't exist
mkdir -p logs

# Check if data_update.py is already running
if ! pgrep -f "python3 data_update.py" > /dev/null; then
    echo "Starting data_update.py..."
    sudo python3 data_update.py > logs/data_update.log 2>&1 &
else
    echo "data_update.py is already running."
fi

# Check if web_server.py is already running
if ! pgrep -f "python3 web_server.py" > /dev/null; then
    echo "Starting web_server.py..."
    sudo python3 web_server.py > logs/web_server.log 2>&1 &
else
    echo "web_server.py is already running."
fi

# Check if light_control.py is already running
if ! pgrep -f "python3 light_control.py" > /dev/null; then
    echo "Starting light_control.py..."
    sudo python3 light_control.py > logs/light_control.log 2>&1 &
else
    echo "light_control.py is already running."
fi

# Print status of running processes
echo "Scripts are running in the background."
