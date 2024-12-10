import sqlite3
from datetime import datetime

# Function to fetch last 24 hours of data from the database
def get_data_from_db():
    conn = sqlite3.connect("sensor_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, temperature, humidity, soil_moisture, cpu_temperature FROM sensor_readings ORDER BY timestamp DESC LIMIT 24")
    rows = cursor.fetchall()
    conn.close()

    timestamps = [datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S").strftime("%H:%M") for row in rows]
    temperatures = [row[1] for row in rows]
    humidities = [row[2] for row in rows]
    soil_moistures = [row[3] for row in rows]
    cpu_temperatures = [row[4] for row in rows]

    return timestamps, temperatures, humidities, soil_moistures, cpu_temperatures
