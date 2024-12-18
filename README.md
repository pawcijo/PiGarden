# PiGarden

PiGarden is a simple web-based application that allows you to monitor environmental data from various sensors, including temperature, humidity, and soil moisture, using a Raspberry Pi. The application stores the sensor readings in an SQLite database and provides real-time data visualization through interactive charts.

## Features
- Real-time sensor data monitoring: Collects temperature, humidity, soil moisture, CPU temperature, and ambient light data.
- Modular services:

    - Light control: Manages garden lighting based on predefined schedules.
    - Irrigation system: Controls the water pump using GPIO relays.
    - Sensor service: Collects sensor data and updates the database.
    - Web service: Provides a dashboard for real-time monitoring and historical data visualization.

- Flexible operation: Run each service individually or simultaneously - using a control script.
- SQLite database: Stores the collected data with timestamps.
- Dark mode: User-friendly toggle to switch between light and dark themes.

#  Components
- Raspberry Pi: The main platform that reads sensor data via I2C.
- SHT31-D Sensor: Measures temperature and humidity.
- SEN0193 Soil Moisture Sensor: An analog sensor that measures the moisture level of the soil.
- ADS7830 ADC Converter: Converts the analog signal from the SEN0193 sensor into a digital value readable via I2C (address 0x48).
- VEML7700 Sensor: Measures lux (light intensity) for plant growth monitoring.
- 230V Lamp: Used to simulate garden lighting. The lamp is controlled by a GPIO relay module.
- Water Pump: Used for irrigation, controlled by GPIO relays. It can be a 12V DC water pump and should have a flow rate of at least 240 liters per hou
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

5. Start the System 
You can start all the services together using the provided start_server.sh script: 
```
./start_server.sh
```

To stop all services, use: 
```
./stop_server.sh
```
Alternatively, you can run each service individually:


Sensor Service:
``` 
python3 SensorServer/data_update.py
```
Light Control: 
```
sudo python3 SensorServer/light_control.py
```
Irrigation System:
``` 
sudo python3 SensorServer/irrigation_system.py
```
Web Service: 
```
    sudo python3 SensorServer/web_server.py
```
 6. Access the Web Dashboard 
 
 Once the web service is running, open a web browser and navigate to your Raspberry Pi’s IP address on port 5000: 
 ```
 http://<your-pi-ip>:5000
 ``` 
 You will see real-time temperature, humidity, soil moisture, and lux readings, as well as graphs showing historical data.
 

# Usage

## Data Collection
Real-Time Data Monitoring: The app collects data from sensors and monitors:

    Temperature
    Humidity
    Soil moisture
    Ambient light (lux)
    Irrigation system status
    CPU temperature

## Light Control 

The lights are automatically controlled based on predefined time settings. The light control is handled by a separate process that ensures the lights are turned off when the control script ends. If the control process is killed (e.g., via pkill), the lights will be turned off automatically.

## Data Visualization
The web interface presents the following charts:
- Temperature Chart: Displays readings from the SHT31-D sensor and CPU temperature.
- Humidity Chart: Displays humidity levels.
- Soil Moisture Chart: Displays soil moisture levels.
- Light Level Chart: Displays ambient light (lux).

The charts are updated in every hour as new data is collected.

## Dark Mode
The app includes a dark mode toggle, which can be activated by clicking the button in the top-right corner.

## Database Schema
The SQLite database `sensor_data.db` contains a table called `sensor_readings` with the following columns:
- id: Auto-incremented primary key.
- timestamp: Date and time of the sensor reading.
- temperature: Temperature value from the SHT31-D sensor.
- humidity: Humidity value from the SHT31-D sensor.
- soil_moisture: Soil moisture level in percentage.
- cpu_temperature: CPU temperature of the Raspberry Pi.
- lux: Ambient light intensity measured by the VEML7700 sensor, stored as a real number.


## Troubleshooting
- I2C Communication Error: Make sure I2C is enabled on your Raspberry Pi and that your sensors are correctly connected.
- Web Interface Not Loading: Ensure Flask is running and accessible from your browser. Check for any errors in the terminal where Flask is running.

## License
This project is open source and available under the MIT License. See the LICENSE file for more details.

## Contributing
Feel free to fork the repository and submit pull requests. Contributions are always welcome!


