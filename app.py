import sqlite3
import smbus
import time
import threading
from flask import Flask, render_template
from datetime import datetime, time as dtime
import pytz
import RPi.GPIO as GPIO

app = Flask(__name__)

# Configuration variables
ADC_ADDRESS = 0x48  # I2C address for ADC
ADC_CHANNEL = 0  # ADC channel for soil moisture
SHT31_ADDRESS = 0x44  # I2C address for SHT31-D sensor
SLEEP_INTERVAL_DATA_PUSH = 3600  # Interval to push data to the database (in seconds)
SLEEP_INTERVAL_LIGHT_CONTROL = 60  # Interval to check light status (in seconds)
LIGHT_ON_HOUR = 23  # Hour to turn lights on (24-hour format)
LIGHT_ON_MINUTE = 50  # Minute to turn lights on
LIGHT_OFF_HOUR = 8  # Hour to turn lights off (24-hour format)
LIGHT_OFF_MINUTE = 0  # Minute to turn lights off
TIMEZONE = "Europe/Warsaw"  # Timezone for local time
TEMP_COMMAND = [0x2C, 0x06]  # Command to read temperature and humidity from SHT31-D
RELAY_CHANNEL = 9  # GPIO pin for the relay controlling the lights

DRY_SOIL_ADC = 191  # ADC value for dry soil
WET_SOIL_ADC = 100  # ADC value for wet soil

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_CHANNEL, GPIO.OUT)

# Turn off lights initially
GPIO.output(RELAY_CHANNEL, GPIO.HIGH)

# Variable to store the current light status
light_status = "OFF"

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect("sensor_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL,
            humidity REAL,
            soil_moisture REAL
        )
    """)
    conn.commit()
    conn.close()

# Function to convert raw ADC value to soil moisture percentage
def convert_to_percentage(raw_value, dry_value=DRY_SOIL_ADC, wet_value=WET_SOIL_ADC):
    """
    Converts the raw ADC value to a soil moisture percentage.
    :param raw_value: Raw ADC value from the ADS7830 (0-255).
    :param dry_value: ADC value corresponding to dry soil (191).
    :param wet_value: ADC value corresponding to wet soil (100).
    :return: Soil moisture percentage (0-100%).
    """
    if raw_value >= dry_value:
        return 0.0  # Completely dry
    elif raw_value <= wet_value:
        return 100.0  # Fully wet
    # Linear interpolation
    percentage = ((dry_value - raw_value) / (dry_value - wet_value)) * 100
    return round(percentage, 2)

# Updated Function to read soil moisture from ADC
def read_soil_moisture(channel, adc_address=ADC_ADDRESS):
    """
    Reads and converts soil moisture raw value to percentage.
    :param channel: ADC channel for the soil moisture sensor.
    :param adc_address: I2C address of the ADC.
    :return: Soil moisture percentage (0-100%).
    """
    bus = smbus.SMBus(1)
    assert 0 <= channel <= 7, "Invalid ADC channel. Must be between 0 and 7."
    command = 0x84 | (channel << 4)
    bus.write_byte(adc_address, command)
    raw_value = bus.read_byte(adc_address)
    return convert_to_percentage(raw_value)

# Function to control lights based on specific hours
def control_lights():
    global light_status
    while True:
        try:
            local_time = datetime.now(pytz.timezone(TIMEZONE)).time()
            light_on_time = dtime(LIGHT_ON_HOUR, LIGHT_ON_MINUTE)
            light_off_time = dtime(LIGHT_OFF_HOUR, LIGHT_OFF_MINUTE)

            if light_on_time <= local_time or local_time < light_off_time:
                GPIO.output(RELAY_CHANNEL, GPIO.LOW)  # Turn light ON
                light_status = "ON"
            else:
                GPIO.output(RELAY_CHANNEL, GPIO.HIGH)  # Turn light OFF
                light_status = "OFF"
        except Exception as e:
            print(f"Error controlling lights: {e}")
        time.sleep(SLEEP_INTERVAL_LIGHT_CONTROL)

# Function to push sensor data to the database every hour
def push_data():
    while True:
        try:
            bus = smbus.SMBus(1)
            bus.write_i2c_block_data(SHT31_ADDRESS, TEMP_COMMAND[0], [TEMP_COMMAND[1]])
            time.sleep(0.5)
            data = bus.read_i2c_block_data(SHT31_ADDRESS, 0x00, 6)

            if len(data) == 6:
                temp = data[0] * 256 + data[1]
                cTemp = -45 + (175 * temp / 65535.0)
                humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
                soil_moisture = read_soil_moisture(ADC_CHANNEL)
                local_time = datetime.now(pytz.timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")

                conn = sqlite3.connect("sensor_data.db")
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO sensor_readings (timestamp, temperature, humidity, soil_moisture) VALUES (?, ?, ?, ?)",
                    (local_time, cTemp, humidity, soil_moisture)
                )
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"Error occurred: {e}")
        time.sleep(SLEEP_INTERVAL_DATA_PUSH)

# Start the background data pushing in a separate thread
data_thread = threading.Thread(target=push_data)
data_thread.daemon = True
data_thread.start()

# Start the background light control in a separate thread
light_thread = threading.Thread(target=control_lights)
light_thread.daemon = True
light_thread.start()

# Route to display sensor data and light status
@app.route("/")
def index():
    conn = sqlite3.connect("sensor_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, temperature, humidity, soil_moisture FROM sensor_readings ORDER BY timestamp DESC LIMIT 24")
    rows = cursor.fetchall()
    conn.close()

    timestamps = []
    for row in rows:
        timestamp = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        timestamps.append(timestamp.strftime("%H:%M"))

    temperatures = [row[1] for row in rows]
    humidities = [row[2] for row in rows]
    soil_moistures = [row[3] for row in rows]

    # Read CPU temperature from the Raspberry Pi
    def get_cpu_temperature():
        try:
            # Read the CPU temperature from the system file
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as temp_file:
                temp = int(temp_file.read()) / 1000.0  # Convert to Celsius
            return temp
        except Exception as e:
            print(f"Error reading CPU temperature: {e}")
            return None

    cpu_temperature = get_cpu_temperature()

    local_timezone = pytz.timezone(TIMEZONE)
    recent_date = datetime.now(local_timezone).strftime("%Y-%m-%d")

    return render_template(
        "index.html",
        timestamps=timestamps,
        temperatures=temperatures,
        humidities=humidities,
        soil_moistures=soil_moistures,
        recent_date=recent_date,
        light_status=light_status,
        cpu_temperature=cpu_temperature  # Pass CPU temperature to the template
    )


if __name__ == "__main__":
    try:
        init_db()
        app.run(debug=False, host="0.0.0.0", port=5000)
    finally:
        GPIO.cleanup()
