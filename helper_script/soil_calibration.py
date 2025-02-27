from smbus2 import SMBus
import time

# Define the I2C address of the ADS7830
ADS7830_ADDRESS = 0x48

# Initialize the I2C bus
bus = SMBus(1)  # Use I2C bus 1

# Read the ADC channel
def read_adc(channel):
    """
    Reads the analog value from the specified ADS7830 channel.
    :param channel: ADC channel (0 to 7)
    :return: ADC value (0 to 255)
    """
    if channel < 0 or channel > 7:
        raise ValueError("Channel must be between 0 and 7")
    
    command = 0x84 | (channel << 4)  # Configure the ADS7830 command for the selected channel
    bus.write_byte(ADS7830_ADDRESS, command)
    return bus.read_byte(ADS7830_ADDRESS)

# Main function
def main():
    try:
        print("Soil Moisture Sensor Calibration Test")
        print("=====================================")
        print("Place the sensor in DRY soil and press Enter...")
        input()  # Wait for user input
        dry_value = read_adc(0)  # Assuming the sensor is connected to channel 0
        print(f"Dry soil ADC value: {dry_value}")
        
        print("\nPlace the sensor in WET soil and press Enter...")
        input()  # Wait for user input
        wet_value = read_adc(0)  # Assuming the sensor is connected to channel 0
        print(f"Wet soil ADC value: {wet_value}")
        
        print("\nOptional: Place the sensor in WATER and press Enter...")
        input()  # Wait for user input
        water_value = read_adc(0)
        print(f"Water ADC value: {water_value}")
        
        print("\nCalibration values:")
        print(f"Dry soil: {dry_value}")
        print(f"Wet soil: {wet_value}")
        print(f"Water (optional): {water_value}")
        
        print("\nUse these values to calibrate your soil moisture readings.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Exiting...")

# Run the main function
if __name__ == "__main__":
    main()
