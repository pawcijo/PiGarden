import eventlet
import socketio
from flask import Flask, render_template
from data_storage import get_data_from_db
from sensor_utils import get_cpu_temperature, read_soil_moisture, read_temperature_humidity, read_lux
from sensor_utils import get_light_status
import psutil
import ssl
import logging
import time  # For delay during restart

# Configure logging
logging.basicConfig(
    filename='logs/web_server.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
)

# Socket.IO server
sio = socketio.Server(cors_allowed_origins="*")
app = Flask(__name__)
flask_app = socketio.WSGIApp(sio, app)

# Sensor and ADC configuration
ADC_CHANNEL = 0

def is_process_running(process_name):
    for process in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
        try:
            if process_name in " ".join(process.info['cmdline']):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

@app.route("/")
def index():
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
        try:
            soil_moisture = read_soil_moisture(ADC_CHANNEL)
            temperature, humidity = read_temperature_humidity()
            cpu_temperature = get_cpu_temperature()
            ambient_light = read_lux()
            light_status = get_light_status()
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
        except Exception as e:
            logging.error(f"Error during data broadcast: {e}")

        eventlet.sleep(10)

# Function to start the WSGI server
def start_server():
    logging.info("Web server starting...")

    # Load SSL certificates
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.load_cert_chain(
        certfile='/etc/letsencrypt/live/pioasis.duckdns.org/fullchain.pem',
        keyfile='/etc/letsencrypt/live/pioasis.duckdns.org/privkey.pem'
    )

    # Start an HTTPS listener
    https_listener = eventlet.listen(('', 443))
    ssl_listener = eventlet.wrap_ssl(
        https_listener,
        certfile='/etc/letsencrypt/live/pioasis.duckdns.org/fullchain.pem',
        keyfile='/etc/letsencrypt/live/pioasis.duckdns.org/privkey.pem'
    )

    # Spawn the data broadcasting process
    eventlet.spawn_n(broadcast_data)

    # Start the WSGI server with SSL and handle errors
    eventlet.wsgi.server(ssl_listener, flask_app)

# Main execution loop to restart the server if it exits
if __name__ == "__main__":
    while True:
        try:
            start_server()
        except Exception as e:
            logging.error(f"Server exited unexpectedly: {e}")
            logging.info("Restarting the server in 5 seconds...")
            time.sleep(5)  # Delay before restarting
