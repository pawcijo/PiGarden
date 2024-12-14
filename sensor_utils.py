import smbus
import time

ADC_ADDRESS = 0x48  # I2C address for ADC
DRY_SOIL_ADC = 174  # ADC value for dry soil
WET_SOIL_ADC = 79  # ADC value for wet soil

SHT31_ADDRESS = 0x44
TEMP_COMMAND = [0x2C, 0x06]

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
    bus = smbus.SMBus(1)
    assert 0 <= channel <= 7, "Invalid ADC channel. Must be between 0 and 7."
    command = 0x84 | (channel << 4)
    bus.write_byte(adc_address, command)
    raw_value = bus.read_byte(adc_address)
    return convert_to_percentage(raw_value)

# Function to read Raspberry Pi CPU temperature
def get_cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as temp_file:
            temp = int(temp_file.read()) / 1000.0  # Convert to Celsius
        return temp
    except Exception as e:
        print(f"Error reading CPU temperature: {e}")
        return None
    
def read_temperature_humidity():
    try:
        bus = smbus.SMBus(1)
        bus.write_i2c_block_data(SHT31_ADDRESS, TEMP_COMMAND[0], [TEMP_COMMAND[1]])
        time.sleep(0.015)
        data = bus.read_i2c_block_data(SHT31_ADDRESS, 0x00, 6)
        temp_raw = (data[0] << 8) | data[1]
        humidity_raw = (data[3] << 8) | data[4]
        return round(-45 + 175 * (temp_raw / 65535.0), 2), round(100 * (humidity_raw / 65535.0), 2)
    except Exception as e:
        print(f"Error reading temperature and humidity: {e}")
        return None, None
