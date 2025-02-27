import os
import time
import board
import adafruit_veml7700
import logging
from smbus2 import SMBus
from datetime import datetime

veml7700 = None

# Constants
ADC_ADDRESS = 0x48  # I2C address for ADC
DRY_SOIL_ADC = 240  # ADC value for dry soil
WET_SOIL_ADC = 76  # ADC value for wet soil
SHT31_ADDRESS = 0x44
TEMP_COMMAND = [0x2C, 0x06]

# Status file path
status_file_path = "/tmp/light_status.txt"

# Set up logging for sensor utils
log_dir = "logs"
log_file = f"{log_dir}/sensor_utils.log"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

sensor_logger = logging.getLogger('sensor_utils')
sensor_logger.setLevel(logging.INFO)

# Create a file handler to write logs to the file
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
sensor_logger.addHandler(file_handler)

# Function to convert raw ADC value to soil moisture percentage
def convert_to_percentage(raw_value, dry_value=DRY_SOIL_ADC, wet_value=WET_SOIL_ADC):
    if raw_value >= dry_value:
        return 0.0  # Completely dry
    elif raw_value <= wet_value:
        return 100.0  # Fully wet
    percentage = ((dry_value - raw_value) / (dry_value - wet_value)) * 100
    return round(percentage, 2)

# Function to read soil moisture from ADC
def read_soil_moisture(channel, adc_address=ADC_ADDRESS):
    bus = SMBus(1)
    assert 0 <= channel <= 7, "Invalid ADC channel. Must be between 0 and 7."
    command = 0x84 | (channel << 4)
    bus.write_byte(adc_address, command)
    raw_value = bus.read_byte(adc_address)
    #sensor_logger.info(f"Read soil moisture from channel {channel}: raw ADC value = {raw_value}")
    return convert_to_percentage(raw_value)

# Function to read Raspberry Pi CPU temperature
def get_cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as temp_file:
            temp = int(temp_file.read()) / 1000.0  # Convert to Celsius
        #sensor_logger.info(f"CPU temperature: {temp}°C")
        return temp
    except Exception as e:
        sensor_logger.error(f"Error reading CPU temperature: {e}")
        return None
    
# Function to read temperature and humidity from SHT31 sensor
def read_temperature_humidity():
    try:
        bus = SMBus(1)
        bus.write_i2c_block_data(SHT31_ADDRESS, TEMP_COMMAND[0], [TEMP_COMMAND[1]])
        time.sleep(0.015)
        data = bus.read_i2c_block_data(SHT31_ADDRESS, 0x00, 6)
        temp_raw = (data[0] << 8) | data[1]
        humidity_raw = (data[3] << 8) | data[4]
        temp = round(-45 + 175 * (temp_raw / 65535.0), 2)
        humidity = round(100 * (humidity_raw / 65535.0), 2)
        #sensor_logger.info(f"Temperature: {temp}°C, Humidity: {humidity}%")
        return temp, humidity
    except Exception as e:
        sensor_logger.error(f"Error reading temperature and humidity: {e}")
        return None, None
    
def get_light_status(path=status_file_path):
        """Get the current light status from the file."""
        if os.path.exists(path):
            with open(path, "r") as status_file:
                light_status = status_file.read().strip()
            #sensor_logger.info(f"Returning light status from file at {path}: {light_status}")
            return light_status
        else:
            #sensor_logger.info(f"Status file not found at {path}. Returning default status: OFF.")
            return "OFF"

# Function to initialize the VEML7700 sensor
def initialize_veml7700():
    global veml7700
    try:
        if veml7700 is not None:
            #sensor_logger.info("VEML7700 is already initialized.")
            return veml7700

        i2c = board.I2C()  # Uses board.SCL and board.SDA
        veml7700 = adafruit_veml7700.VEML7700(i2c)
        
        veml7700.light_gain = veml7700.ALS_GAIN_1_8  # Try changing the gain value
        veml7700.integration_time = 100  # Try increasing the integration time to 100ms
        
        #sensor_logger.info("VEML7700 sensor initialized successfully.")
        return veml7700
    except Exception as e:
        sensor_logger.error(f"Error initializing VEML7700 sensor: {e}")
        return None

def read_lux():
    global veml7700
    try:
        if veml7700 is None:
            veml7700 = initialize_veml7700()

        if veml7700:
            raw_light = veml7700.lux  # Raw lux value for ambient light
            #sensor_logger.info(f"Raw light reading: {raw_light}")
            ambient_light = round(raw_light, 2)  # Processed lux value
            #sensor_logger.info(f"Processed ambient light reading: {ambient_light} lux")
            return ambient_light
        else:
            sensor_logger.error("VEML7700 sensor is not initialized.")
            return None
    except Exception as e:
        sensor_logger.error(f"Error reading ambient light: {e}")
        return None