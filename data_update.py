import smbus
import time
from datetime import datetime
import sqlite3
import pytz
from sensor_utils import read_soil_moisture, get_cpu_temperature, read_temperature_humidity

# Constants
SLEEP_INTERVAL = 3600  # Interval to push data to the database (in seconds)

# Function to push data into the database
def push_data():
    while True:
        try:
            # Read temperature and humidity from SHT31 sensor
            cTemp, humidity = read_temperature_humidity()

            if cTemp is not None and humidity is not None:
                # Read other sensor values
                soil_moisture = read_soil_moisture(0)  # Using channel 0 for soil moisture
                cpu_temperature = get_cpu_temperature()
                local_time = datetime.now(pytz.timezone("Europe/Warsaw")).strftime("%Y-%m-%d %H:%M:%S")

                # Store data in the database
                conn = sqlite3.connect("sensor_data.db")
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO sensor_readings (timestamp, temperature, humidity, soil_moisture, cpu_temperature)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (local_time, cTemp, humidity, soil_moisture, cpu_temperature),
                )
                conn.commit()
                conn.close()

        except Exception as e:
            print(f"Error occurred: {e}")

        time.sleep(SLEEP_INTERVAL)  # Wait before the next update

if __name__ == "__main__":
    push_data()
