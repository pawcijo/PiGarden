from smbus2 import SMBus
import time

# Initialize I2C
bus = SMBus(1)  # Use I2C bus 1
sht31_address = 0x44  # Default I2C address for SHT31-D

# Function to send a command to the sensor
def send_command(command):
    """
    Sends a command to the SHT31-D sensor.
    :param command: The command to send (2 bytes).
    """
    bus.write_i2c_block_data(sht31_address, command[0], command[1:])

# Function to read temperature and humidity
def read_temperature_humidity():
    """
    Reads temperature and humidity from the SHT31-D sensor.
    :return: A tuple (temperature, humidity).
    """
    # Send measurement command
    send_command([0x2C, 0x06])  # High repeatability measurement command
    time.sleep(0.015)  # Wait for measurement to complete (15ms)

    # Read 6 bytes of data (temperature MSB, LSB, CRC, humidity MSB, LSB, CRC)
    data = bus.read_i2c_block_data(sht31_address, 0x00, 6)

    # Extract temperature and humidity
    temp_raw = (data[0] << 8) | data[1]
    humidity_raw = (data[3] << 8) | data[4]

    # Calculate temperature in Celsius
    temperature = -45 + (175 * (temp_raw / 65535.0))

    # Calculate relative humidity in %
    humidity = 100 * (humidity_raw / 65535.0)

    return temperature, humidity

# Main execution
if __name__ == "__main__":
    try:
        # Read and display temperature and humidity once
        temperature, humidity = read_temperature_humidity()
        print(f"Temperature: {temperature:.2f} °C")
        print(f"Humidity: {humidity:.2f} %")
    except Exception as e:
        print(f"An error occurred: {e}")
