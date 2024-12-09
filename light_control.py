import time
import os
import RPi.GPIO as GPIO
from datetime import datetime, time as dtime
import pytz
import threading
import signal
import sys

RELAY_CHANNEL = 9  # GPIO pin for the relay controlling the lights
LIGHT_ON_HOUR = 22  # Hour to turn lights on (24-hour format)
LIGHT_ON_MINUTE = 50  # Minute to turn lights on
LIGHT_OFF_HOUR = 8  # Hour to turn lights off (24-hour format)
LIGHT_OFF_MINUTE = 0  # Minute to turn lights off
SLEEP_INTERVAL_LIGHT_CONTROL = 60  # Interval to check light status (in seconds)

HEARTBEAT_FILE = "/tmp/light_control_heartbeat.txt"  # Temporary heartbeat file

# GPIO setup should be done only once
def setup_gpio():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_CHANNEL, GPIO.OUT)
    GPIO.output(RELAY_CHANNEL, GPIO.HIGH)  # Turn off lights initially

# Variable to store the current light status
light_status = "OFF"

def control_lights():
    """Control the light based on time."""
    global light_status
    while True:
        try:
            local_time = datetime.now(pytz.timezone("Europe/Warsaw")).time()
            light_on_time = dtime(LIGHT_ON_HOUR, LIGHT_ON_MINUTE)
            light_off_time = dtime(LIGHT_OFF_HOUR, LIGHT_OFF_MINUTE)

            if light_on_time <= local_time or local_time < light_off_time:
                GPIO.output(RELAY_CHANNEL, GPIO.LOW)  # Turn light ON
                light_status = "ON"
            else:
                GPIO.output(RELAY_CHANNEL, GPIO.HIGH)  # Turn light OFF
                light_status = "OFF"
            write_heartbeat()  # Update heartbeat every cycle
        except Exception as e:
            print(f"Error controlling lights: {e}")
        time.sleep(SLEEP_INTERVAL_LIGHT_CONTROL)

def write_heartbeat():
    """Function to update the heartbeat file periodically."""
    with open(HEARTBEAT_FILE, 'w') as f:
        f.write(str(time.time()))  # Store the current time as the heartbeat

def get_light_status():
    """Function to get the current light status."""
    return light_status

def start_control_lights_thread():
    """Start the light control in a separate thread."""
    light_thread = threading.Thread(target=control_lights)
    light_thread.daemon = True
    light_thread.start()

def turn_off_lights():
    """Function to turn off the lights manually."""
    GPIO.output(RELAY_CHANNEL, GPIO.HIGH)  # Turn light OFF

def signal_handler(sig, frame):
    """Handle cleanup and ensure lights are off when the process is terminated."""
    print("Process terminated. Cleaning up GPIO and turning off lights.")
    GPIO.cleanup()
    turn_off_lights()
    sys.exit(0)

if __name__ == "__main__":
    setup_gpio()  # Set up GPIO initially
    start_control_lights_thread()  # Start the light control in a separate thread

    # Register signal handler for termination
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        while True:
            time.sleep(60)  # Keep the script running
    except KeyboardInterrupt:
        GPIO.cleanup()  # Clean up GPIO when exiting
