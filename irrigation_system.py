import time
from gpiozero import OutputDevice
import schedule
import logging
from datetime import datetime
import os

# Define relay channel for irrigation
relay_ch = OutputDevice(24, active_high=False, initial_value=False)

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

def water_plants(duration):
    """
    Function to water plants by turning the relay on for a specified duration.
    :param duration: Duration in seconds for which the pump should run.
    """
    try:
        logging.info(f"Starting the pump for {duration} seconds.")
        relay_ch.on()  # Turn on the pump
        time.sleep(duration)  # Keep the pump running
        logging.info("Stopping the pump.")
        relay_ch.off()  # Turn off the pump
    except Exception as e:
        logging.error(f"An error occurred while watering: {e}")

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
    watering_times = ["06:00","22:00"]  # Adjust times as needed
    watering_duration = 15  # Duration in seconds for each session

    # Schedule watering
    schedule_watering(watering_times, watering_duration)

    # Keep script running to check the schedule
    logging.info("Irrigation system started. Press Ctrl+C to exit.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)  # Avoid busy waiting
    except KeyboardInterrupt:
        logging.info("Exiting irrigation system.")
        logging.info("Irrigation system stopped.")
