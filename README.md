# PiGarden

PiGarden is a simple web-based application that allows you to monitor environmental data from various sensors, including temperature, humidity, and soil moisture, using a Raspberry Pi. The application stores the sensor readings in an SQLite database and provides real-time data visualization through interactive charts.

## Features
- Real-time sensor data monitoring: Collects temperature, humidity, soil moisture, and CPU temperature data.
- SQLite database: Stores the collected data with timestamps.
- Web interface: View your data using an interactive dashboard built with Flask and Chart.js.
- Data storage and persistence: Historical data is stored in an SQLite database, making it easy to analyze trends over time.
- Light control: Automatically manages the lights based on time, with manual overrides through the web interface.
- Watchdog: A heartbeat mechanism ensures that the lights are turned off if the light control process is killed.



#  Components
- Raspberry Pi: The main platform that reads sensor data via I2C.
- SHT31-D Sensor: Measures temperature and humidity.
- SEN0193 Soil Moisture Sensor: An analog sensor that measures the moisture level of the soil.
- ADS7830 ADC Converter: Converts the analog signal from the SEN0193 sensor into a digital value readable via I2C (address 0x48).
- Flask: A lightweight Python web framework used to display the data in a web browser.
- Chart.js: A JavaScript library used to create interactive line charts for visualizing the data.
- Light control process: Manages the lighting of the garden based on time and manual override.
- Watchdog process: Monitors the status of the light control process and ensures the lights are turned off if the process fails.

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
Connect the SHT31-D sensor and SEN0193 soil moisture sensor to your Raspberry Pi.

##### SHT31-D Sensor:

    I2C address: 0x44
    Ensure the wiring is correct:
    
        SDA to GPIO 2 (pin 3)
        SCL to GPIO 3 (pin 5)
        VCC to 3.3V
        GND to GND
    
SEN0193 Soil Moisture Sensor with ADS7830:

The SEN0193 sensor outputs an analog voltage proportional to the soil moisture level.

Use the ADS7830 ADC to convert the analog signal into a digital value for the Raspberry Pi.

ADS7830 wiring:
 ```
- VCC to 3.3V or 5V.
- GND to GND.
- SDA to GPIO 2 (pin 3).
- SCL to GPIO 3 (pin 5).
```

SEN0193 wiring:
```
- VCC to 3.3V.
- GND to GND.
- Signal (analog output) to one of the ADC input channels on the ADS7830 (e.g., CH0)
```
Ensure the wiring is correct:
```
- SDA to GPIO 2 (pins 3 or line)
- SCL to GPIO 3 (pins 5 or line)
- VCC to 3.3V
- GND to GND
```

###### Soil Moisture Sensor Calibration

⚠️⚠️⚠️ Soil sensor should be calibrated, more instructions in [Sensor Calibration](https://github.com/pawcijo/PiGarden/tree/main/helper_script/soil_sensor_calibration.md)

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

## Light Control 

The lights are automatically controlled based on predefined time settings (e.g., on at 10:50 PM, off at 8:00 AM). The light control is handled by a separate process that ensures the lights are turned off when the control script ends. If the control process is killed (e.g., via pkill), the lights will be turned off automatically.

## Data Visualization
The web interface presents the following charts:
- Temperature Chart: Displays temperature readings from the SHT31-D sensor and CPU temperature over time.
- Humidity Chart: Displays humidity readings over time.
- Soil Moisture Chart: Displays soil moisture levels over time.

The charts are updated in real-time as new data is collected.

## Dark Mode
The app includes a dark mode toggle, which can be activated by clicking the button in the top-right corner.

## File Structure
```
PiGarden/
│
├── SensorServer/
│   ├── data_storage.py     # Script for storing sensor data
│   ├── data_update.py      # Script for updating sensor data
│   ├── init_database.py    # Script for initializing the database
│   ├── light_control.py    # Script for controlling lights with a heartbeat mechanism
│   ├── sensor_utils.py     # Utility functions for sensor management
│   └── web_server.py       # Main Flask web server
│
├── helper_script/          # Helper scripts directory
├── logs/                   # Directory for logs
├── requirements.txt        # Python dependencies
├── sensor_data.db          # SQLite database where sensor data is stored
└── README.md               # This README file
```

## Database Schema
The SQLite database `sensor_data.db` contains a table called `sensor_readings` with the following columns:
- id: Auto-incremented primary key.
- timestamp: Date and time of the sensor reading.
- temperature: Temperature value from the SHT31-D sensor.
- humidity: Humidity value from the SHT31-D sensor.
- soil_moisture: Soil moisture level in percentage.
- cpu_temperature: CPU temperature of the Raspberry Pi.


## Troubleshooting
- I2C Communication Error: Make sure I2C is enabled on your Raspberry Pi and that your sensors are correctly connected.
- Web Interface Not Loading: Ensure Flask is running and accessible from your browser. Check for any errors in the terminal where Flask is running.

## License
This project is open source and available under the MIT License. See the LICENSE file for more details.

## Contributing
Feel free to fork the repository and submit pull requests. Contributions are always welcome!


