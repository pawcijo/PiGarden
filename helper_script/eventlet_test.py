import eventlet
import socketio
import smbus  # For I2C communication with the ADC
import time

# Create a Socket.IO server
sio = socketio.Server(cors_allowed_origins="*")  # Allow all origins
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

clients = 0

# ADC and sensor configuration
ADC_ADDRESS = 0x48  # I2C address for ADC
ADC_CHANNEL = 0     # ADC channel connected to the sensor
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

# Background task to broadcast a message every second
def broadcast_message():
    while True:
        soil_moisture = read_soil_moisture(ADC_CHANNEL)
        if soil_moisture is not None:
            sio.emit('broadcast', {'description': f'Soil Moisture: {soil_moisture}%'})
        else:
            sio.emit('broadcast', {'description': 'Error reading sensor data.'})
        eventlet.sleep(1)  # Non-blocking sleep

if __name__ == '__main__':
    # Start the broadcast message in a background thread
    eventlet.spawn_n(broadcast_message)  # Non-blocking background task
    print("Starting server on port 8080...")
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app)
