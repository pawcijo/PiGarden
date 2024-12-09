from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random
import time

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

def generate_real_time_data():
    while True:
        # Simulate sensor data
        data = {
            'temperature': random.uniform(20.0, 30.0),
            'humidity': random.uniform(30.0, 60.0),
            'soil_moisture': random.uniform(10.0, 60.0),
            'cpu_temperature': random.uniform(40.0, 60.0)
        }
        # Emit the data to all connected clients
        socketio.emit('sensor_data', data)
        time.sleep(2)  # Update every 2 seconds

if __name__ == '__main__':
    # Start generating data in the background
    socketio.start_background_task(generate_real_time_data)
    socketio.run(app, host='0.0.0.0', port=5000)
