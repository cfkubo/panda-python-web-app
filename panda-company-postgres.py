import logging
from flask import Flask, render_template
import psycopg2
import folium
import os
import configparser
import inspect
import sys

config = configparser.ConfigParser()
config.read('config.py')

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

db_config = {
    "host": config.get('postgres', 'pg_host'),
    "port": config.get('postgres', 'pg_port'),
    "database": config.get('postgres', 'pg_database'),
    "user": config.get('postgres', 'pg_user'),
    "password": config.get('postgres', 'pg_password'),
}


@app.route('/')
def home():
    return render_template('vhome.html')


def fetch_vehicle_data():
    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM vehicles")
            data = cur.fetchall()
            logging.info(f"Fetched {len(data)} vehicle records")
            return data


@app.route('/vechiles')
def index():
    vehicle_data = fetch_vehicle_data()
    return render_template('read.html', data=vehicle_data)


def fetch_emp_data():
    with psycopg2.connect(**db_config) as conn1:
        with conn1.cursor() as curr:
            curr.execute("SELECT * FROM employees")
            empdata = curr.fetchall()
            logging.info(f"Fetched {len(empdata)} employee records")
            return empdata


@app.route('/employees')
def emp():
    emp_data = fetch_emp_data()
    return render_template('read-emp.html', empdata=emp_data)


def fetch_car_data():
    with psycopg2.connect(**db_config) as conn1:
        with conn1.cursor() as curr:
            curr.execute("SELECT * FROM car_models")
            car_models = curr.fetchall()
            logging.info(f"Fetched {len(car_models)} car model records")
            return car_models


@app.route('/car_models')
def car_models():
    car_models_data = fetch_car_data()
    return render_template('car_models.html', car_models=car_models_data)


def fetch_vehicle_locations():
    """Fetches vehicle GPS locations from the database."""
    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT latitude, longitude FROM vehicles")
            locations = cur.fetchall()
            logging.info(f"Fetched {len(locations)} vehicle locations")
            return locations


def create_folium_map(locations):
    """Creates a Folium map with markers at the specified locations."""

    m = folium.Map(location=[39.8282, -98.5795], zoom_start=6)  # Adjust initial location and zoom

    for lat, lon in locations:
        folium.Marker([lat, lon], popup=f"Lat: {lat}, Lon: {lon}").add_to(m)

    return m


@app.route('/iot')
def map():
    locations = fetch_vehicle_locations()
    logging.info(f"Creating map with {len(locations)} locations")
    m = create_folium_map(locations)
    m.save("templates/vehicle_locations-new.html")
    # return render_template('vehicle_locations-new.html', iot_html=m._repr_html_())
    return render_template('vehicle_locations-new.html', m=m._repr_html_())

def get_db_version():
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        cur.close()
        conn.close()
        print(version)
        return version
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

@app.route('/env')
def env():
    imports = []
    for name, module in globals().items():
        if inspect.ismodule(module):
            imports.append(f"import {name}")
    version = get_db_version()
    sytem_versions=sys.version
    print(version)
    return render_template('env-details.html', version=version ,imports=imports ,sytem_versions=sytem_versions)


@app.route('/alerts')
def alerts():
    alerts_data = fetch_alerts_data()
    return render_template('alerts.html', alerts=alerts_data)

def fetch_alerts_data():
    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as curr:
            curr.execute("SELECT o.name AS ownername, v.make, v.model, o.email, o.phone, v.vehicle_alerts, v.next_service_date FROM owners o INNER JOIN vehicles v ON o.name = v.ownername where vehicle_alerts != '{NULL}'")
            alerts = curr.fetchall()
            for row in alerts:
                print(row)
            return alerts

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
