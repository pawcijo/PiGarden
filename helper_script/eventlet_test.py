import eventlet
import socketio
import smbus  # For I2C communication with the ADC
import time
from eventlet.green import os

# Create a Socket.IO server
sio = socketio.Server(cors_allowed_origins="*")  # Allow all origins

# Serve static files (index.html)
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': os.path.join(os.getcwd(), 'templates', 'index.html')}
})

clients = 0

# ADC and sensor configuration
ADC_ADDRESS = 0x48  # I2C address for ADC
ADC_CHANNEL = 0     # ADC channel connected to the soil moisture sensor
SHT31_ADDRESS = 0x44  # I2C address for SHT31-D sensor
TEMP_COMMAND = [0x2C, 0x06]  # Command to read temperature and humidity from SHT31-D
DRY_SOIL_ADC = 191  # ADC value for dry soil
WET_SOIL_ADC = 100  # ADC value for wet soil

# Function to convert ADC value to soil moisture percentage
def convert_to_percentage(raw_value, dry_value=DRY_SOIL_ADC, wet_value=WET_SOIL_ADC):
    if raw_value >= dry_value:
        return 0.0  # Completely dry
    elif raw_value <= wet_value:
        return 100.0  # Fully wet
    percentage = ((dry_value - raw_value) / (dry_value - wet_value)) * 100
    return round(percentage, 2)

# Function to read soil moisture from the ADC
def read_soil_moisture(channel, adc_address=ADC_ADDRESS):
    try:
        bus = smbus.SMBus(1)  # Use I2C bus 1
        assert 0 <= channel <= 7, "Invalid ADC channel. Must be between 0 and 7."
        command = 0x84 | (channel << 4)
        bus.write_byte(adc_address, command)
        raw_value = bus.read_byte(adc_address)
        return convert_to_percentage(raw_value)
    except Exception as e:
        print(f"Error reading soil moisture: {e}")
        return None

# Function to read temperature and humidity from SHT31-D sensor
def read_temperature_humidity():
    try:
        bus = smbus.SMBus(1)
        bus.write_i2c_block_data(SHT31_ADDRESS, TEMP_COMMAND[0], [TEMP_COMMAND[1]])
        time.sleep(0.015)  # Wait for the measurement to complete
        data = bus.read_i2c_block_data(SHT31_ADDRESS, 0x00, 6)

        if len(data) == 6:
            temp_raw = (data[0] << 8) | data[1]
            temperature = -45 + (175 * (temp_raw / 65535.0))

            humidity_raw = (data[3] << 8) | data[4]
            humidity = 100 * (humidity_raw / 65535.0)

            return round(temperature, 2), round(humidity, 2)
    except Exception as e:
        print(f"Error reading temperature and humidity: {e}")
        return None, None

# Function to read Raspberry Pi CPU temperature
def get_cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as temp_file:
            temp = int(temp_file.read()) / 1000.0  # Convert to Celsius
        return round(temp, 2)
    except Exception as e:
        print(f"Error reading CPU temperature: {e}")
        return None

@sio.event
def connect(sid, environ):
    global clients
    clients += 1
    print(f"Client connected! SID: {sid}, Total clients: {clients}")
    # Send a welcome message to the newly connected client
    sio.emit('newclientconnect', {'description': 'Hey, welcome!'}, room=sid)

@sio.event
def disconnect(sid):
    global clients
    clients -= 1
    print(f"Client disconnected! SID: {sid}, Total clients: {clients}")

@sio.event
def my_message(sid, data):
    print(f"Message from {sid}: {data}")
    # Echo the received message back to the sender
    sio.emit('message', {'data': data}, room=sid)

# Background task to broadcast sensor data every second
def broadcast_data():
    while True:
        soil_moisture = read_soil_moisture(ADC_CHANNEL)
        temperature, humidity = read_temperature_humidity()
        cpu_temperature = get_cpu_temperature()

        if soil_moisture is not None and temperature is not None and humidity is not None and cpu_temperature is not None:
            sio.emit('broadcast', {
                'description': f"Soil Moisture: {soil_moisture}%, "
                               f"Temperature: {temperature}°C, "
                               f"Humidity: {humidity}%, "
                               f"CPU Temp: {cpu_temperature}°C"
            })
        else:
            sio.emit('broadcast', {'description': 'Error reading sensor data.'})

        eventlet.sleep(1)  # Non-blocking sleep

if __name__ == '__main__':
    # Start the broadcast task in the background
    eventlet.spawn_n(broadcast_data)  # Non-blocking background task
    print("Starting server on port 8080...")
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app)
