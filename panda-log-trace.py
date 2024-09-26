import logging
from flask import Flask, render_template
import psycopg2
import folium
import os
import configparser

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
    return render_template('vehicle_locations-new.html', iot_html=m._repr_html_())


if __name__ == "__main__":
    app.run(debug=True)
