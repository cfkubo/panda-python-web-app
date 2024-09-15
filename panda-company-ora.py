from flask import Flask, render_template
import folium
import os
import configparser
import db_config
import oracledb
import sys
import platform
import inspect
import math



config = configparser.ConfigParser()
config.read('config.py')

app = Flask(__name__)


# db_config = {
#     "host": config.get('postgres', 'pg_host'),
#     "port": config.get('postgres', 'pg_port'),
#     "database": config.get('postgres', 'pg_database'),
#     "user": config.get('postgres', 'pg_user'),
#     "password": config.get('postgres', 'pg_password'),
# }



@app.route('/')
def home():
    return render_template('vhome.html')

def fetch_vehicle_data():
    with oracledb.connect(user=db_config.user, password=db_config.pw, dsn=db_config.dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM vehicles")
            data = cur.fetchall()
            return data

@app.route('/vechiles')
def index():
    vehicle_data = fetch_vehicle_data()
    return render_template('read.html', data=vehicle_data)

def fetch_emp_data():
    with oracledb.connect(user=db_config.user, password=db_config.pw, dsn=db_config.dsn) as conn1:
        with conn1.cursor() as curr:
            curr.execute("SELECT * FROM employees")
            empdata = curr.fetchall()
            for row in empdata:
                print(row)
            return empdata

@app.route('/employees')
def emp():
    emp_data = fetch_emp_data()
    return render_template('read-emp.html', empdata=emp_data)


def fetch_car_data():
    with oracledb.connect(user=db_config.user, password=db_config.pw, dsn=db_config.dsn) as conn1:
        with conn1.cursor() as curr:
            curr.execute("SELECT * FROM car_models")
            car_models = curr.fetchall()
            for row in car_models:
                print(row)
            return car_models

@app.route('/car_models')
def car_models():
    car_models_data = fetch_car_data()
    return render_template('car_models.html', car_models=car_models_data)


def fetch_vehicle_locations():
    """Fetches vehicle GPS locations from the database."""
    with oracledb.connect(user=db_config.user, password=db_config.pw, dsn=db_config.dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT latitude, longitude FROM vehicles")
            locations = cur.fetchall()
            return locations

def create_folium_map(locations):
    """Creates a Folium map with markers at the specified locations."""

    m = folium.Map(location=[39.8282, -98.5795], zoom_start = 6)  # Adjust initial location and zoom

    for lat, lon in locations:
        folium.Marker([lat, lon], popup=f"Lat: {lat}, Lon: {lon}").add_to(m)

    return m

@app.route('/iot')
def map():
    locations = fetch_vehicle_locations()
    print(locations)
    m = create_folium_map(locations)
    m.save("templates/vehicle_locations-new.html")
    return render_template('vehicle_locations-new.html', iot_html=m._repr_html_())

# @app.route('/env')
# def env()
#     con = oracledb.connect(user=db_config.user, password=db_config.pw, dsn=db_config.dsn)
#     print("Database version:", con.version)

@app.route('/alerts')
def alerts():
    alerts_data = fetch_alerts_data()
    return render_template('alerts.html', alerts=alerts_data)

def fetch_alerts_data():
    with oracledb.connect(user=db_config.user, password=db_config.pw, dsn=db_config.dsn) as conn1:
        with conn1.cursor() as curr:
            curr.execute("SELECT o.name AS ownername, v.make, v.model, o.email, o.phone, v.vehicle_alerts, v.next_service_date FROM arul.owners o INNER JOIN arul.vehicles v ON o.name = v.ownername where vehicle_alerts != '{NULL}'")
            alerts = curr.fetchall()
            for row in alerts:
                print(row)
            return alerts

@app.route('/env')
def env():
    imports = []
    for name, module in globals().items():
        if inspect.ismodule(module):
            imports.append(f"import {name}")
    sytem_versions=sys.version
    try:
        con = oracledb.connect(user=db_config.user, password=db_config.pw, dsn=db_config.dsn)
        database_version = con.version  # Get database version
        con.close()
        return render_template('env.html', database_version=database_version, sytem_versions=sytem_versions , imports=imports)  # Pass version to template
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return render_template('env.html', database_version=None)  # Pass None for error handling

# def print_imports():
#     for name, module in globals().items():
#         if inspect.ismodule(module):
#             print(f"import {name}")
#
# print_imports()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(debug=True,host='0.0.0.0', port=port)
