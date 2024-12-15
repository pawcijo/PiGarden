import os
import time
from datetime import datetime
import sqlite3
import pytz
import logging
from sensor_utils import (
    read_soil_moisture,
    get_cpu_temperature,
    read_temperature_humidity,
    read_lux,
)

# Constants
SLEEP_INTERVAL = 3600  # Interval to push data to the database (in seconds)

# Set up logging
log_dir = "logs"
log_file = f"{log_dir}/data_update.log"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger = logging.getLogger('data_update')
logger.setLevel(logging.INFO)

# Create a file handler to write logs to the file
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Function to push data into the database
def push_data():
    while True:
        try:
            time.sleep(10) #sleep 10 s to let sensor wake up
            soil_moisture = read_soil_moisture(0)  # Using channel 0 for soil moisture
            cTemp, humidity = read_temperature_humidity()
            cpu_temperature = get_cpu_temperature()
            lux = read_lux()
            local_time = datetime.now(pytz.timezone("Europe/Warsaw")).strftime("%Y-%m-%d %H:%M:%S")
            # Store data in the database
            conn = sqlite3.connect("sensor_data.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO sensor_readings (timestamp, temperature, humidity, soil_moisture, cpu_temperature, lux)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (local_time, cTemp, humidity, soil_moisture, cpu_temperature, lux),
            )
            conn.commit()
            conn.close()

            # Log the data update
            logger.info(f"Data logged at {local_time}:")
            logger.info(f"  Temperature: {cTemp}°C, Humidity: {humidity}%, Soil Moisture: {soil_moisture}%, CPU Temp: {cpu_temperature}°C, Lux: {lux} lx")

        except Exception as e:
            # Log any errors that occur
            logger.error(f"Error occurred: {e}")

        time.sleep(SLEEP_INTERVAL)  # Wait before the next update

if __name__ == "__main__":
    push_data()
