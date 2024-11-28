# PiGarden

PiGarden is a simple web-based application that allows you to monitor environmental data from various sensors, including temperature, humidity, and soil moisture, using a Raspberry Pi. The application stores the sensor readings in an SQLite database and provides real-time data visualization through interactive charts.

## Features
- Real-time sensor data monitoring: Collects temperature, humidity, and soil moisture data.
- SQLite database: Stores the collected data with timestamps.
- Web interface: View your data using an interactive dashboard built with Flask and Chart.js.
- Data storage and persistence: Historical data is stored in an SQLite database, making it easy to analyze trends over time.

#  Components
- Raspberry Pi: The main platform that reads sensor data via I2C.
- SHT31-D Sensor: Measures temperature and humidity.
- Soil Moisture Sensor: Measures the moisture level of the soil (connected via I2C address 0x48).
- Flask: A lightweight Python web framework used to display the data in a web browser.
- Chart.js: A JavaScript library used to create interactive line charts for visualizing the data.

## Installation

1. Set up your Raspberry Pi
Ensure your Raspberry Pi is running Raspberry Pi OS and has I2C enabled. You can enable I2C through the Raspberry Pi configuration tool:
sudo raspi-config
Under "Interfacing Options", select "I2C" and enable it.

2. Install Dependencies
Clone the repository to your Raspberry Pi:
```
git clone https://github.com/pawcijo/PiGarden.git
cd PiGarden
```

Install the required Python packages:
```
pip install -r requirements.txt
```

3. Set up the Database
Run the script to initialize the SQLite database and create the table that will store sensor data.
```
python init_db.py
```
This will create a sensor_data.db file with the necessary structure.

4. Connect Sensors
Connect the SHT31-D sensor and soil moisture sensor to your Raspberry Pi using the I2C interface:
- SHT31-D should be connected to I2C address 0x44.
- Soil moisture sensor should be connected to I2C address 0x48.

Ensure the wiring is correct:
- SDA to GPIO 2 (pins 3)
- SCL to GPIO 3 (pins 5)
- VCC to 3.3V
- GND to GND

5. Start the Application
To start the Flask application:
```
python app.py
```
The application will run on http://0.0.0.0:5000/. You can access it through your Raspberry Pi's IP address.

6. View Data
Open a web browser and navigate to your Raspberry Pi’s IP address on port 5000:
```
http://<your-pi-ip>:5000
```
You will see real-time temperature, humidity, and soil moisture readings, as well as graphs showing historical data.

# Usage

## Data Collection
The app collects data at regular intervals (every hour) and stores it in the database. Data is inserted into the sensor_readings table with a timestamp. The application also calculates soil moisture percentage and stores it in the same table.

## Data Visualization
The web interface presents the following charts:
- Temperature Chart: Displays temperature readings over time.
- Humidity Chart: Displays humidity readings over time.
- Soil Moisture Chart: Displays soil moisture levels over time.

The charts are updated in real-time as new data is collected.

## Dark Mode
The app includes a dark mode toggle, which can be activated by clicking the button in the top-right corner.

## File Structure
```
PiGarden/
│
├── app.py            # Main Flask application
├── init_db.py        # Script to initialize the database
├── requirements.txt  # List of Python dependencies
├── templates/
│   ├── index.html    # HTML template for the web interface
└── sensor_data.db    # SQLite database where sensor data is stored
```

## Database Schema
The SQLite database sensor_data.db contains a table called sensor_readings with the following columns:
- id: Auto-incremented primary key.
- timestamp: Date and time of the sensor reading.
- temperature: Temperature value from the SHT31-D sensor.
- humidity: Humidity value from the SHT31-D sensor.
- soil_moisture: Soil moisture level in percentage.

## Troubleshooting
- I2C Communication Error: Make sure I2C is enabled on your Raspberry Pi and that your sensors are correctly connected.
- Web Interface Not Loading: Ensure Flask is running and accessible from your browser. Check for any errors in the terminal where Flask is running.

## License
This project is open source and available under the MIT License. See the LICENSE file for more details.

## Contributing
Feel free to fork the repository and submit pull requests. Contributions are always welcome!


