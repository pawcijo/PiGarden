import sqlite3

def initialize_database():
    """Initialize the sensor_data database with all required fields."""
    try:
        conn = sqlite3.connect("sensor_data.db")
        cursor = conn.cursor()

        # Create a new table with all fields if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL,
            humidity REAL,
            soil_moisture REAL,
            cpu_temperature REAL,
            lux REAL
        );
        """)

        conn.commit()
        print("Database initialized with all fields!")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    initialize_database()
