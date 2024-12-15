import sqlite3
from datetime import datetime

# Function to fetch last 24 hours of data from the database
def get_data_from_db():
    conn = sqlite3.connect("sensor_data.db")
    cursor = conn.cursor()
    
    # Fetch timestamp, temperature, humidity, soil moisture, CPU temperature, and lux from the database
    cursor.execute("""
        SELECT timestamp, temperature, humidity, soil_moisture, cpu_temperature, lux 
        FROM sensor_readings 
        ORDER BY timestamp DESC 
        LIMIT 24
    """)
    
    rows = cursor.fetchall()
    conn.close()

    # Parse and format the data
    timestamps = [datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S").strftime("%H:%M") for row in rows]
    temperatures = [row[1] for row in rows]
    humidities = [row[2] for row in rows]
    soil_moistures = [row[3] for row in rows]
    cpu_temperatures = [row[4] for row in rows]
    lux_values = [row[5] for row in rows]  # Extract lux values

    return timestamps, temperatures, humidities, soil_moistures, cpu_temperatures, lux_values
