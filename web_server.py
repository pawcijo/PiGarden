import eventlet
import socketio
from flask import Flask, render_template
from data_storage import get_data_from_db
from sensor_utils import get_cpu_temperature, read_soil_moisture, read_temperature_humidity, read_lux
from light_control import get_light_status  # Reads this from file, in the future use interprocess communication
import smbus
import time
from datetime import datetime
import pytz
import logging

# Configure logging
logging.basicConfig(
    filename='logs/web_server.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'  # Include function name in log
)

# Socket.IO server
sio = socketio.Server(cors_allowed_origins="*")
app = Flask(__name__)
flask_app = socketio.WSGIApp(sio, app)

# ADC and Sensor configuration
ADC_ADDRESS = 0x48
ADC_CHANNEL = 0
DRY_SOIL_ADC = 191
WET_SOIL_ADC = 100
SHT31_ADDRESS = 0x44
TEMP_COMMAND = [0x2C, 0x06]

@app.route("/")
def index():
    # Fetch historical data from the database
    timestamps, temperatures, humidities, soil_moistures, cpu_temperatures, lux_values = get_data_from_db()

    return render_template(
        "index.html",
        timestamps=timestamps,
        temperatures=temperatures,
        humidities=humidities,
        soil_moistures=soil_moistures,
        cpu_temperatures=cpu_temperatures,
        lux_values=lux_values
    )

@sio.event
def connect(sid, environ):
    logging.info(f"Client connected: {sid}")
    sio.emit('newclientconnect', {'description': 'Welcome to the dashboard!'}, room=sid)

@sio.event
def disconnect(sid):
    logging.info(f"Client disconnected: {sid}")

def broadcast_data():
    while True:
        soil_moisture = read_soil_moisture(ADC_CHANNEL)
        temperature, humidity = read_temperature_humidity()
        cpu_temperature = get_cpu_temperature()
        ambient_light = read_lux()  # Only retrieve ambient_light, ignore white_light
        light_status = get_light_status()  # Get light status from shared memory

        sio.emit('broadcast', {
            'soil_moisture': soil_moisture,
            'temperature': temperature,
            'humidity': humidity,
            'cpu_temperature': cpu_temperature,
            'lux': ambient_light,
            'light_status': light_status  # Include light status in broadcast
        })

        logging.info(f"Broadcasting data: Soil Moisture={soil_moisture}%, Temperature={temperature}°C, "
                     f"Humidity={humidity}%, CPU Temp={cpu_temperature}°C, Lux={ambient_light}, Light Status={light_status}")
        
        eventlet.sleep(10)

if __name__ == "__main__":
    logging.info("Web server starting...")
    eventlet.spawn_n(broadcast_data)
    eventlet.wsgi.server(eventlet.listen(('', 5000)), flask_app)
