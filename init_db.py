import sqlite3

try:
    # Create SQLite database and table
    conn = sqlite3.connect("sensor_data.db")
    cursor = conn.cursor()

    # Create a new table with temperature, humidity, and soil_moisture columns
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sensor_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        temperature REAL,
        humidity REAL,
        soil_moisture REAL  -- New column for soil moisture
    );
    """)

    conn.commit()
    print("Database initialized and new table created!")
except sqlite3.Error as e:
    print(f"Error initializing database: {e}")
finally:
    conn.close()
