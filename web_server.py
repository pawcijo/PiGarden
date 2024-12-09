from flask import Flask, render_template
from data_storage import get_data_from_db  # Function to fetch data from the database
from sensor_utils import get_cpu_temperature  # Function to get CPU temperature
from light_control import get_light_status  # Import the function to get light status
import sqlite3
from datetime import datetime
import pytz

app = Flask(__name__)

@app.route("/")
def index():
    # Fetch last 24 hours of data from the database for the graph
    timestamps, temperatures, humidities, soil_moistures, cpu_temperatures = get_data_from_db()

    # Fetch the current CPU temperature from the Raspberry Pi
    current_cpu_temperature = get_cpu_temperature()

    # Get the current light status from the light control script
    light_status = get_light_status()

    local_timezone = pytz.timezone("Europe/Warsaw")
    recent_date = datetime.now(local_timezone).strftime("%Y-%m-%d")

    return render_template(
        "index.html",
        timestamps=timestamps,
        temperatures=temperatures,
        humidities=humidities,
        soil_moistures=soil_moistures,
        cpu_temperatures=cpu_temperatures,  # Pass CPU temperatures for graph
        cpu_temperature=current_cpu_temperature,  # Pass the current CPU temperature for display
        recent_date=recent_date,
        light_status=light_status  # Pass the current light status
    )

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
