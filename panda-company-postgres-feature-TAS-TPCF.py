# import logging
from flask import Flask, render_template, request, jsonify
import psycopg2
import folium
import os
import configparser
import inspect
import sys
import db_config
import requests
import json
import subprocess
from ollama import Client
import logging
import signal
import re


app = Flask(__name__)

env_vars = os.getenv('VCAP_SERVICES')
pg_service = json.loads(env_vars)['postgres'][0]
jdbc_url = pg_service['credentials']['jdbcUrl']

# Regular expression pattern to match the JDBC URL components
pattern = r"jdbc:postgresql://([^:/]+):(\d+)/([^?]+)\?user=([^&]+)&password=([^&]+)"

# Match the pattern against the JDBC URL
match = re.match(pattern, jdbc_url)

if match:
    # Extract the captured groups
    pg_host = match.group(1)
    pg_port = int(match.group(2))
    pg_database = match.group(3)
    pg_user = match.group(4)
    pg_password = match.group(5)

# print(f"Host: {pg_host}")
# print(f"Port: {pg_port}")
# print(f"Database: {pg_database}")
# print(f"Username: {pg_user}")
# print(f"Password: {pg_password}")


pg_config = {
    "host": pg_host,
    "port": pg_port,
    "database": pg_database,
    "user": pg_user,
    "password": pg_password,
}

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

@app.route('/')
def home():
    return render_template('vhome.html')


def fetch_vehicle_data():
    with psycopg2.connect(**pg_config) as conn:
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
    with psycopg2.connect(**pg_config) as conn1:
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
    with psycopg2.connect(**pg_config) as conn1:
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
    with psycopg2.connect(**pg_config) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT latitude, longitude, vehicle_alerts FROM vehicles")
            locations = cur.fetchall()
            logging.info(f"Fetched {len(locations)} vehicle locations")
            print (locations)
            return locations


def create_folium_map(locations):
    """Creates a Folium map with markers at the specified locations."""

    m = folium.Map(location=[55, -172], zoom_start=3)  # Adjust initial location and zoom

    for lat, lon in locations:
        folium.Marker([lat, lon], popup=f"Lat: {lat}, Lon: {lon}, Alert: {vehicle_alerts}").add_to(m)
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
        conn = psycopg2.connect(**pg_config)
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
    with psycopg2.connect(**pg_config) as conn:
        with conn.cursor() as curr:
            curr.execute("SELECT o.name AS ownername, v.make, v.model, o.email, o.phone, v.vehicle_alerts, v.next_service_date FROM owners o INNER JOIN vehicles v ON o.name = v.ownername where vehicle_alerts != '{NULL}'")
            alerts = curr.fetchall()
            for row in alerts:
                print(row)
            return alerts

# Replace with your Google Maps API key
api_key = db_config.google_api_key
#db_config.google_api_key

@app.route('/geo')
def geo():
    return render_template('gg.html')

@app.route('/geocode', methods=['POST'])
def geocode():
    address = request.form['address']

    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    response = requests.get(url)
    data = response.json()
    print("Sent:", json.dumps(data))

    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        latitude = location['lat']
        longitude = location['lng']
        with psycopg2.connect(**pg_config) as conn1:
            with conn1.cursor() as curr:
                # Use parameter substitution for latitude and longitude
                sql = """
                    SELECT latitude, longitude
                    FROM vehicles
                    ORDER BY ABS(CAST(latitude AS numeric) - %s) ASC , ABS(CAST(longitude AS numeric) - %s) ASC
                    LIMIT 10;
                """

                # Execute the query with variables
                curr.execute(sql, (latitude, longitude))

                findpanda_data = curr.fetchall()
                logging.info(f"Fetched {len(findpanda_data)} findpanda_data records")
                print(findpanda_data)
                logging.info(f"Creating map with {len(findpanda_data)} locations")
                m = create_folium_map(findpanda_data)
                m.save("templates/panda_fleet_near_you.html")
                # return render_template('vehicle_locations-new.html', iot_html=m._repr_html_())
                return render_template('panda_fleet_near_you.html', m=m._repr_html_())


                # return render_template('pandanearme.html', findpanda_data=findpanda_data)
                # return findpanda_data
                # return jsonify({'latitude': latitude, 'longitude': longitude})
    else:
        return jsonify({'error': 'Address not found'}), 404

def execute_sql_file(file_path, db_config):
    with open(file_path, 'r') as f:
        sql = f.read()

    with psycopg2.connect(**pg_config) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()

@app.route('/sql_loader')
def sql_loader():
    file_path = 'sql/demo.sql'
    sql_loader = execute_sql_file(file_path, db_config)
    # sql_loader = execute_sql_file()
    return redirect(url_for('home'))

@app.route('/drop_tables')
def drop_tables():
    file_path = 'sql/droptables.sql'
    sql_loader = execute_sql_file(file_path, db_config)
    # sql_loader = execute_sql_file()
    return render_template('sql_loader.html')


# @app.route('/data_loader')
# def data_loader():
#     subprocess.run(["python", "data-generators/vechile-data-generator-new.py"])
#     return render_template('sql_loader.html')

@app.route('/data_loader')
def data_loader():
    return render_template('sql_loader.html')

# Add routes for start and stop functionality (adjust URLs as needed)
@app.route('/start_consumers', methods=['POST'])
def start_loading_process():
    print('started')
    global subprocess  # Access the global subprocess variable
    print('hello from starting Consumers')
    subprocess = subprocess.run(["sh", "start-consumers.sh"])
    print('GINI Producers Applications started !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    return render_template('sql_loader.html')
    # return
@app.route('/start_producers', methods=['POST'])
def start_consumers_process():
    print('started')
    global subprocess1  # Access the global subprocess variable
    print('hello from starting Producers')
    subprocess1 = subprocess.run(["sh", "start-producers.sh"])
    print('GINI Consumers Applications started !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    return render_template('sql_loader.html')

@app.route('/stop_gini')
def stop_consumers_process():
    os.killpg(os.getpgid(subprocess.pid), signal.SIGTERM)
    os.killpg(os.getpgid(subprocess1.pid), signal.SIGTERM)
# Function to start and stop the subprocess
# def start_data_loading():
#     global subprocess  # Access the global subprocess variable
#     print('hello from start data loading')
#     subprocess = subprocess.run(["sh", "start-consumers.sh"])
#     return 'Consumers started !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    # return redirect(url_for('home'))
    # return home()

# def start_consumers():
#     global subprocess1  # Access the global subprocess variable
#     print('hello from consumers')
#     subprocess1 = subprocess.run1(["sh", "start-producers.sh"])
#     print('producers started !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
#     # return redirect(url_for('home'))
#     return home()
# def stop_data_loading():
#     global subprocess  # Access the global subprocess variable
#     print('hello from STOP data loading')
#     subprocess = subprocess.terminate()
#     return "Data loading stopped!"

client = Client(host=db_config.LLM_URL)
model = db_config.MODEL
# print(model)

@app.route('/llama', methods=['GET', 'POST'])
def llama():
    if request.method == 'POST':
        question = request.form['question']
        response = client.chat(model=model, messages=[
            {'role': 'user', 'content': question}
        ])
        answer = response['message']['content']
        print(answer)
        return render_template('ollama.html', question=question, answer=answer, model=model)
    else:
        return render_template('ollama.html', model=model)



if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
