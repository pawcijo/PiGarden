import eventlet
import socketio
from flask import Flask, render_template
from data_storage import get_data_from_db
from sensor_utils import get_cpu_temperature, read_soil_moisture, read_temperature_humidity, read_lux
from sensor_utils import get_light_status
import psutil
import smbus
import time
from datetime import datetime
import pytz
import logging
import ssl

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

def is_process_running(process_name):
    for process in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
        try:
            # Check if the process name matches or appears in the command line
            if process_name in " ".join(process.info['cmdline']):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


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
        irrigation_system_status = is_process_running("irrigation_system.py")

        sio.emit('broadcast', {
            'soil_moisture': soil_moisture,
            'temperature': temperature,
            'humidity': humidity,
            'cpu_temperature': cpu_temperature,
            'lux': ambient_light,
            'light_status': light_status,
            'irrigation_system_status': irrigation_system_status 
        })

        eventlet.sleep(10)

if __name__ == "__main__":
    logging.info("Web server starting...")
    
    # Load SSL certificates
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(certfile='/etc/letsencrypt/live/pioasis.duckdns.org/fullchain.pem', keyfile='/etc/letsencrypt/live/pioasis.duckdns.org/privkey.pem')

    eventlet.spawn_n(broadcast_data)

    # Use SSL context to start the server on HTTPS
    listener = eventlet.listen(('', 443))
    ssl_listener = eventlet.wrap_ssl(listener, certfile='/etc/letsencrypt/live/pioasis.duckdns.org/fullchain.pem', keyfile='/etc/letsencrypt/live/pioasis.duckdns.org/privkey.pem')

    # Start the WSGI server with SSL
    eventlet.wsgi.server(ssl_listener, flask_app)
