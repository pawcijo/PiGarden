import os
import time
from gpiozero import OutputDevice
from datetime import datetime, time as dtime
import pytz
import threading
import signal
import sys
import logging

# Relay GPIO pin configuration
RELAY_CHANNEL = 9  # GPIO pin for the relay controlling the lights

# Light control schedule
LIGHT_ON_HOUR = 20  # Hour to turn lights on (24-hour format)
LIGHT_ON_MINUTE = 10  # Minute to turn lights on
LIGHT_OFF_HOUR = 8  # Hour to turn lights off (24-hour format)
LIGHT_OFF_MINUTE = 0  # Minute to turn lights off (24-hour format)

SLEEP_INTERVAL_LIGHT_CONTROL = 60  # Interval to check light status (in seconds)

# Set up logging for light control
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

light_logger = logging.getLogger("light_control")
light_logger.setLevel(logging.DEBUG)

light_handler = logging.FileHandler(os.path.join(log_dir, "light_control.log"))
light_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"))
light_logger.addHandler(light_handler)

# Status file path
status_file_path = "/tmp/light_status.txt"

# Light control relay setup using gpiozero
light_relay = OutputDevice(RELAY_CHANNEL, active_high=False, initial_value=False)  # Relay OFF initially


def control_lights():
    """Control the lights based on time."""
    while True:
        try:
            # Get current local time
            local_time = datetime.now(pytz.timezone("Europe/Warsaw")).time()
            light_on_time = dtime(LIGHT_ON_HOUR, LIGHT_ON_MINUTE)
            light_off_time = dtime(LIGHT_OFF_HOUR, LIGHT_OFF_MINUTE)

            # Determine if the lights should be ON
            if light_on_time <= light_off_time:  # Same-day schedule
                is_light_on = light_on_time <= local_time < light_off_time
            else:  # Overnight schedule
                is_light_on = local_time >= light_on_time or local_time < light_off_time

            # Control the light relay
            if is_light_on:
                if not light_relay.value:  # Only turn on if it's off
                    light_relay.on()
                    set_light_status("ON")
                    light_logger.info("Lights turned ON.")
            else:
                if light_relay.value:  # Only turn off if it's on
                    light_relay.off()
                    set_light_status("OFF")
                    light_logger.info("Lights turned OFF.")

            # Debugging log for time and state
            light_logger.debug(f"Local time: {local_time}, Light ON: {is_light_on}")

        except Exception as e:
            light_logger.error(f"Error controlling lights: {e}")

        time.sleep(SLEEP_INTERVAL_LIGHT_CONTROL)

def set_light_status(status, file_path=status_file_path):
    """Set the light status in the temporary file."""
    try:
        with open(file_path, "w") as f:
            f.write(status)
    except Exception as e:
        light_logger.error(f"Error updating light status file: {e}")

def start_control_lights_thread():
    """Start the light control loop in a separate thread."""
    light_thread = threading.Thread(target=control_lights)
    light_thread.daemon = True
    light_thread.start()


def turn_off_lights():
    """Turn off the lights manually."""
    light_relay.off()
    set_light_status("OFF")
    light_logger.info("Lights turned OFF manually.")


def signal_handler(sig, frame):
    """Handle cleanup when the process is terminated."""
    light_logger.info("Process terminated. Turning off lights and cleaning up.")
    turn_off_lights()
    sys.exit(0)


if __name__ == "__main__":
    # Start the light control in a separate thread
    start_control_lights_thread()

    # Register signal handler for safe termination
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        while True:
            time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        light_logger.info("Script interrupted. Turning off lights and exiting.")
        turn_off_lights()
