#!/bin/bash

# Create a logs directory if it doesn't exist
mkdir -p logs

# Check if irrigation_system.py is already running
if ! pgrep -f "python3 irrigation_system.py" > /dev/null; then
    echo "Starting irrigation_system.py..."
    sudo python3 irrigation_system.py > logs/irrigation_system.log 2>&1 &
else
    echo "irrigation_system.py is already running."
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
