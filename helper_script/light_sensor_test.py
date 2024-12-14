import time
import board
import adafruit_veml7700

# Initialize the I2C connection
i2c = board.I2C()  # Uses board.SCL and board.SDA
veml7700 = adafruit_veml7700.VEML7700(i2c)

# Display descriptions of the sensor's data
print("VEML7700 Sensor Data:")
print("----------------------------------------------------------")
print("1. Ambient Light (lux):")
print("   The primary light measurement in lux, representing the")
print("   amount of visible light detected by the sensor.")
print()
print("2. White Light (raw):")
print("   A raw measurement representing white light intensity,")
print("   which may include some infrared light sensitivity.")
print()
print("3. Gain Setting:")
print("   The current light gain multiplier. Smaller gains are")
print("   useful in bright conditions, while larger gains improve")
print("   sensitivity in low-light environments.")
print()
print("4. Integration Time:")
print("   The duration the sensor measures light for each reading,")
print("   which determines accuracy and sensitivity. Longer times")
print("   improve accuracy in low-light conditions.")
print()
print("5. Resolution (lux):")
print("   The minimum detectable light change based on current")
print("   gain and integration settings.")
print()
print("----------------------------------------------------------\n")

# Configure the sensor for demonstration
veml7700.light_gain = 1  # Set gain (options: 1, 1/2, 1/4)
veml7700.integration_time = 100  # Set integration time in ms (options: 25, 50, 100, etc.)


# Collect data from the sensor
ambient_light = veml7700.lux
white_light = veml7700.white
gain = veml7700.gain_value()
integration_time = veml7700.integration_time_value()
resolution = veml7700.resolution()
shutdown_status = veml7700.light_shutdown

# Display the readings
print("Ambient Light (lux): {:.2f}".format(ambient_light))
print("White Light (raw): {}".format(white_light))
print("Current Gain: {}".format(gain))
print("Integration Time: {} ms".format(integration_time))
print("Resolution: {:.5f} lux".format(resolution))
print("Shutdown Status: {}".format("ON" if shutdown_status else "OFF"))
print("----------------------------------------------------------\n")

