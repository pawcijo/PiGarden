import time
import RPi.GPIO as GPIO
import schedule
import logging
from datetime import datetime
import os

# Define relay channel
relay_ch = 24

# Create logs directory if it doesn't exist
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Configure logging
log_file = os.path.join(log_dir, "irrigation_system.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(relay_ch, GPIO.OUT)
GPIO.output(relay_ch, GPIO.HIGH)  # Ensure the pump is off initially

def water_plants(duration):
    """
    Function to water plants by turning the relay on for a specified duration.
    :param duration: Duration in seconds for which the pump should run.
    """
    try:
        logging.info(f"Starting the pump for {duration} seconds.")
        GPIO.output(relay_ch, GPIO.LOW)  # Turn on the pump
        time.sleep(duration)            # Keep the pump running
        logging.info("Stopping the pump.")
        GPIO.output(relay_ch, GPIO.HIGH)  # Turn off the pump
    except Exception as e:
        logging.error(f"An error occurred while watering: {e}")
    finally:
        GPIO.cleanup()
        logging.info("Watering process complete.")

def schedule_watering(times, duration):
    """
    Schedule watering tasks at specific times.
    :param times: List of times in "HH:MM" format.
    :param duration: Duration in seconds for each watering session.
    """
    for watering_time in times:
        schedule.every().day.at(watering_time).do(water_plants, duration=duration)
        logging.info(f"Scheduled watering at {watering_time} for {duration} seconds.")

if __name__ == "__main__":
    # Define watering schedule and duration
    watering_times = ["06:00", "18:00"]  # Adjust times as needed
    watering_duration = 10  # Duration in seconds for each session

    # Schedule watering
    schedule_watering(watering_times, watering_duration)

    # Keep script running to check the schedule
    logging.info("Irrigation system started. Press Ctrl+C to exit.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)  # Avoid busy waiting
    except KeyboardInterrupt:
        logging.info("Exiting irrigation system. Cleaning up GPIO...")
        GPIO.cleanup()
        logging.info("Irrigation system stopped.")
