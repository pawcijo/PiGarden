import sqlite3
import smbus
import time
import threading
from flask import Flask, render_template
from datetime import datetime
import pytz

app = Flask(__name__)

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

# Function to read soil moisture from ADC
def read_soil_moisture(channel, adc_address=0x48):
    """
    Reads soil moisture value from the ADC.
    :param channel: ADC channel to read (0-7).
    :param adc_address: I2C address of the ADC.
    :return: Soil moisture percentage (0-100%).
    """
    bus = smbus.SMBus(1)
    assert 0 <= channel <= 7, "Invalid ADC channel. Must be between 0 and 7."
    command = 0x84 | (channel << 4)  # ADC channel selection command
    bus.write_byte(adc_address, command)
    adc_value = bus.read_byte(adc_address)  # Read raw ADC value (0-255)
    
    # Convert ADC value to percentage
    soil_moisture = (adc_value / 255.0) * 100
    return soil_moisture

# Function to push sensor data to the database every hour
def push_data():
    while True:
        try:
            # Read temperature and humidity from SHT31-D
            bus = smbus.SMBus(1)
            sht31_address = 0x44
            bus.write_i2c_block_data(sht31_address, 0x2C, [0x06])
            time.sleep(0.5)
            data = bus.read_i2c_block_data(sht31_address, 0x00, 6)

            if len(data) == 6:
                temp = data[0] * 256 + data[1]
                cTemp = -45 + (175 * temp / 65535.0)
                humidity = 100 * (data[3] * 256 + data[4]) / 65535.0

                # Read soil moisture from ADC channel 0
                soil_moisture = read_soil_moisture(0)

                # Get current local time
                local_time = datetime.now(pytz.timezone("Europe/Warsaw")).strftime("%Y-%m-%d %H:%M:%S")

                # Insert data into database with local timestamp
                conn = sqlite3.connect("sensor_data.db")
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO sensor_readings (timestamp, temperature, humidity, soil_moisture) VALUES (?, ?, ?, ?)",
                    (local_time, cTemp, humidity, soil_moisture)
                )
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"Error occurred: {e}")  # Print the error for debugging purposes

        # Wait for 1 hour before pushing data again
        time.sleep(3600)

# Start the background data pushing in a separate thread
thread = threading.Thread(target=push_data)
thread.daemon = True  # Ensures the thread stops when the program stops
thread.start()

# Route to display sensor data
@app.route("/")
def index():
    conn = sqlite3.connect("sensor_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, temperature, humidity, soil_moisture FROM sensor_readings ORDER BY timestamp DESC LIMIT 24")
    rows = cursor.fetchall()
    conn.close()

    # Use timestamps as they are (no conversion)
    timestamps = []
    for row in rows:
        # Parse the timestamp from the database (assumed to be in Europe/Warsaw timezone)
        timestamp = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")

        # Format to show only hour and minute (HH:MM)
        timestamps.append(timestamp.strftime("%H:%M"))

    temperatures = [row[1] for row in rows]
    humidities = [row[2] for row in rows]
    soil_moistures = [row[3] for row in rows]

    # Get current date in local timezone
    local_timezone = pytz.timezone("Europe/Warsaw")
    recent_date = datetime.now(local_timezone).strftime("%Y-%m-%d")

    return render_template(
        "index.html",
        timestamps=timestamps,
        temperatures=temperatures,
        humidities=humidities,
        soil_moistures=soil_moistures,
        recent_date=recent_date
    )

if __name__ == "__main__":
    init_db()
    app.run(debug=False, host="0.0.0.0", port=5000)
