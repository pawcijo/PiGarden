import os
import time
import RPi.GPIO as GPIO
from datetime import datetime, time as dtime
import pytz
import threading
import signal
import sys
import logging

RELAY_CHANNEL = 9  # GPIO pin for the relay controlling the lights
LIGHT_ON_HOUR = 22  # Hour to turn lights on (24-hour format)
LIGHT_ON_MINUTE = 50  # Minute to turn lights on
LIGHT_OFF_HOUR = 8  # Hour to turn lights off (24-hour format)
LIGHT_OFF_MINUTE = 0  # Minute to turn lights off (24-hour format)
SLEEP_INTERVAL_LIGHT_CONTROL = 60  # Interval to check light status (in seconds)

# Set up logging for light control
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Create a logger for light control
light_logger = logging.getLogger('light_control')
light_logger.setLevel(logging.DEBUG)

# Create a file handler to write logs to a file
light_handler = logging.FileHandler(os.path.join(log_dir, 'light_control.log'))
light_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'))
light_logger.addHandler(light_handler)

# Define path for the status file in /tmp directory
status_file_path = "/tmp/light_status.txt"

# GPIO setup should be done only once
def setup_gpio():
    try:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RELAY_CHANNEL, GPIO.OUT)
        GPIO.output(RELAY_CHANNEL, GPIO.HIGH)  # Turn off lights initially
        light_logger.info("GPIO setup completed successfully.")
    except Exception as e:
        light_logger.error(f"Error setting up GPIO: {e}")

def control_lights():
    """Control the light based on time."""
    while True:
        try:
            local_time = datetime.now(pytz.timezone("Europe/Warsaw")).time()
            light_on_time = dtime(LIGHT_ON_HOUR, LIGHT_ON_MINUTE)
            light_off_time = dtime(LIGHT_OFF_HOUR, LIGHT_OFF_MINUTE)

            if light_on_time <= local_time or local_time < light_off_time:
                GPIO.output(RELAY_CHANNEL, GPIO.LOW)  # Turn light ON
                with open(status_file_path, 'w') as status_file:
                    status_file.write('ON')  # Write status to file
                light_logger.info("Light turned ON.")
            else:
                GPIO.output(RELAY_CHANNEL, GPIO.HIGH)  # Turn light OFF
                with open(status_file_path, 'w') as status_file:
                    status_file.write('OFF')  # Write status to file
                light_logger.info("Light turned OFF.")
        except Exception as e:
            light_logger.error(f"Error controlling lights: {e}")
        time.sleep(SLEEP_INTERVAL_LIGHT_CONTROL)

def set_light_status(status, file_path=status_file_path):
    """Set the light status in the temporary file."""
    try:
        with open(file_path, 'w') as f:
            f.write(status)
    except Exception as e:
        light_logger.error(f"Error updating light status file: {e}")

def get_light_status(path=status_file_path):
    """Function to get the current light status as a string ('ON' or 'OFF').
    
    If no path is provided, the default is /tmp/light_status.txt.
    """
    if os.path.exists(path):
        with open(path, 'r') as status_file:
            light_status = status_file.read().strip()
        light_logger.info(f"Returning light status from file at {path}: {light_status}")
        return light_status
    else:
        # Return 'OFF' if the file does not exist
        light_logger.info(f"Status file not found at {path}. Returning default status: OFF.")
        return 'OFF'

def start_control_lights_thread():
    """Start the light control in a separate thread."""
    light_thread = threading.Thread(target=control_lights)
    light_thread.daemon = True
    light_thread.start()

def turn_off_lights():
    """Function to turn off the lights manually."""
    GPIO.output(RELAY_CHANNEL, GPIO.HIGH)  # Turn light OFF
    set_light_status("OFF")  # Update light status to 'OFF'
    light_logger.info("Light turned OFF manually.")

def signal_handler(sig, frame):
    """Handle cleanup and ensure lights are off when the process is terminated."""
    light_logger.info("Process terminated. Cleaning up GPIO and turning off lights.")
    turn_off_lights()
    GPIO.cleanup()
    sys.exit(0)

if __name__ == "__main__":
    setup_gpio()  # Set up GPIO initially
    start_control_lights_thread()  # Start the light control in a separate thread

    # Register signal handler for termination
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        while True:
            time.sleep(1)  # Keep the process running
    except KeyboardInterrupt:
        turn_off_lights()
        light_logger.info("Script interrupted and GPIO cleaned up.")
