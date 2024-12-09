import smbus
import time
from datetime import datetime
import sqlite3
from sensor_utils import read_soil_moisture, get_cpu_temperature
import pytz

ADC_ADDRESS = 0x48  # I2C address for ADC
SHT31_ADDRESS = 0x44  # I2C address for SHT31-D sensor
SLEEP_INTERVAL = 3600  # Interval to push data to the database (in seconds)

# Function to push data into the database
def push_data():
    while True:
        try:
            bus = smbus.SMBus(1)
            # Read temperature and humidity data from SHT31 sensor
            bus.write_i2c_block_data(SHT31_ADDRESS, 0x2C, [0x06])
            time.sleep(0.5)
            data = bus.read_i2c_block_data(SHT31_ADDRESS, 0x00, 6)

            if len(data) == 6:
                temp = data[0] * 256 + data[1]
                cTemp = -45 + (175 * temp / 65535.0)
                humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
                soil_moisture = read_soil_moisture(0)  # Using channel 0 for soil moisture
                cpu_temperature = get_cpu_temperature()
                local_time = datetime.now(pytz.timezone("Europe/Warsaw")).strftime("%Y-%m-%d %H:%M:%S")

                # Store data in the database
                conn = sqlite3.connect("sensor_data.db")
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sensor_readings (timestamp, temperature, humidity, soil_moisture, cpu_temperature)
                    VALUES (?, ?, ?, ?, ?)
                """, (local_time, cTemp, humidity, soil_moisture, cpu_temperature))
                conn.commit()
                conn.close()

        except Exception as e:
            print(f"Error occurred: {e}")

        time.sleep(SLEEP_INTERVAL)  # Wait before the next update

if __name__ == "__main__":
    push_data()
