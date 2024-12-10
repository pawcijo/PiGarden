import eventlet
import socketio
from flask import Flask, render_template
from data_storage import get_data_from_db
from sensor_utils import get_cpu_temperature, read_soil_moisture, read_temperature_humidity
from light_control import get_light_status
import smbus
import time
from datetime import datetime
import pytz

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
    timestamps, temperatures, humidities, soil_moistures, cpu_temperatures = get_data_from_db()
    current_cpu_temperature = get_cpu_temperature()
    light_status = get_light_status()
    local_timezone = pytz.timezone("Europe/Warsaw")
    recent_date = datetime.now(local_timezone).strftime("%Y-%m-%d")

    return render_template(
        "index.html",
        timestamps=timestamps,
        temperatures=temperatures,
        humidities=humidities,
        soil_moistures=soil_moistures,
        cpu_temperatures=cpu_temperatures,
        cpu_temperature=current_cpu_temperature,
        recent_date=recent_date,
        light_status=light_status
    )

@sio.event
def connect(sid, environ):
    print(f"Client connected: {sid}")
    sio.emit('newclientconnect', {'description': 'Welcome to the dashboard!'}, room=sid)

@sio.event
def disconnect(sid):
    print(f"Client disconnected: {sid}")

def broadcast_data():
    while True:
        soil_moisture = read_soil_moisture(ADC_CHANNEL)
        temperature, humidity = read_temperature_humidity()
        cpu_temperature = get_cpu_temperature()

        sio.emit('broadcast', {
            'soil_moisture': soil_moisture,
            'temperature': temperature,
            'humidity': humidity,
            'cpu_temperature': cpu_temperature
        })
        eventlet.sleep(1)

if __name__ == "__main__":
    eventlet.spawn_n(broadcast_data)
    eventlet.wsgi.server(eventlet.listen(('', 5000)), flask_app)
