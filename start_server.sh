#!/bin/bash

# Create a logs directory if it doesn't exist
mkdir -p logs

# Run data_update.py in the background with logging
echo "Starting data_update.py..."
sudo python3 data_update.py > logs/server.log 2>&1 &

# Run web_server.py in the background with logging
echo "Starting web_server.py..."
sudo python3 web_server.py > logs/web_server.log 2>&1 &

# Run light_control.py in the background with logging
echo "Starting light_control.py..."
sudo python3 light_control.py > logs/light_control.log 2>&1 &

# Print status of running processes
echo "Scripts are running in the background."