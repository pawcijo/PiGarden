import smbus
import time

# Constants
I2C_BUS = 1  # I2C bus number (usually 1 for Raspberry Pi)
ADC_ADDRESS = 0x48  # I2C address of ADS7830
CHANNEL = 0  # ADC channel for the soil moisture sensor

# Calibration values
DRY_SOIL = 191
WET_SOIL = 100
WATER = 95  # Optional (used for reference if needed)

def read_adc(channel, adc_address=ADC_ADDRESS):
    """
    Reads the raw analog value from the specified channel of the ADS7830.
    :param channel: ADC channel to read (0-7).
    :param adc_address: I2C address of the ADS7830.
    :return: Raw ADC value (0-255).
    """
    assert 0 <= channel <= 7, "Invalid ADC channel. Must be between 0 and 7."
    command = 0x84 | (channel << 4)  # ADS7830 command format
    bus = smbus.SMBus(I2C_BUS)
    bus.write_byte(adc_address, command)
    raw_value = bus.read_byte(adc_address)
    return raw_value

def convert_to_percentage(raw_value, dry_value=DRY_SOIL, wet_value=WET_SOIL):
    """
    Converts the raw ADC value to a soil moisture percentage.
    :param raw_value: Raw ADC value from the ADS7830 (0-255).
    :param dry_value: ADC value corresponding to dry soil.
    :param wet_value: ADC value corresponding to wet soil.
    :return: Soil moisture percentage (0-100%).
    """
    # Ensure values are in the correct range
    if raw_value >= dry_value:
        return 0.0  # Completely dry
    elif raw_value <= wet_value:
        return 100.0  # Fully wet
    
    # Linear interpolation to calculate percentage
    percentage = ((dry_value - raw_value) / (dry_value - wet_value)) * 100
    return round(percentage, 2)

# Main script
if __name__ == "__main__":
    try:
        while True:
            # Read the raw ADC value
            raw_value = read_adc(CHANNEL)
            
            # Convert to soil moisture percentage
            soil_moisture_percentage = convert_to_percentage(raw_value)
            
            print(f"Raw ADC Value: {raw_value}, Soil Moisture: {soil_moisture_percentage}%")
            
            # Wait before the next reading
            time.sleep(1)
    except KeyboardInterrupt:
        print("Script stopped.")
