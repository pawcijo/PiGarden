#!/bin/bash

# Find and kill the python processes running for each script
echo "Stopping data_update.py..."
pkill -f data_update.py

echo "Stopping web_server.py..."
pkill -f web_server.py

echo "Stopping light_control.py..."
pkill -f light_control.py

echo "Stopping irrigation_system.py..."
pkill -f irrigation_system.py

# Confirm processes are killed
echo "All specified scripts have been stopped."
