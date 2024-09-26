import pika
import json
import configparser
import psycopg2
from psycopg2.extensions import register_adapter, AsIs
import db_config

config = configparser.ConfigParser()
config.read('config.py')
rabbitmq_host = db_config.rabbitmq_host
rabbitmq_port = db_config.rabbitmq_port
rabbitmq_user = db_config.rabbitmq_user
rabbitmq_password = db_config.rabbitmq_password # Handle potential errors
rabbitmq_queue = config.get('rabbitmq', 'rabbitmq_queue')

def connect_to_rabbitmq(host='your_rabbitmq_host', queue_name=rabbitmq_queue):
    """Establishes a connection to RabbitMQ."""

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
    )
    channel = connection.channel()

    return channel, connection

def connect_to_postgres():
    """Establishes a connection to PostgreSQL using configuration."""

    try:
        # Access configuration values
        pg_host = config.get('postgres', 'pg_host')
        pg_database = config.get('postgres', 'pg_database')
        pg_user = config.get('postgres', 'pg_user')
        pg_password = config.get('postgres', 'pg_password')

        connection = psycopg2.connect(
            host=pg_host,
            database=pg_database,
            user=pg_user,
            password=pg_password
        )
        return connection
    except (Exception, psycopg2.Error) as error:
        print(f"Error connecting to PostgreSQL: {error}")
        return None  # Indicate connection failure

def insert_item_data(conn, item_data):
    """Inserts data into the vehicles_new table."""

    cursor = conn.cursor()
    sql = """
        INSERT INTO vehicles_new (make, model, gps_location, ownername, mileage, fuel_level, temperature, serviced_date, next_service_date, vehicle_alerts)
        VALUES (%s, %s, (POINT(%s)), %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        item_data['make'],
        item_data['model'],
        item_data['gps-location'],
        item_data['owner-name'],
        item_data['mileage'],
        item_data['fuel_level'],
        item_data['temperature'],
        item_data['serviced_date'],
        item_data['next_service_date'],
        item_data['vehicle_alerts']
    ))
    conn.commit()
    cursor.close()
    print(f"Inserted item data: {item_data}")

def main():
    """Main function that connects to RabbitMQ and PostgreSQL, processes data, and inserts it into the table."""

    rabbitmq_channel, rabbitmq_connection = connect_to_rabbitmq()

    def callback(ch, method, properties, body):
        data = json.loads(body)
        try:
            postgres_conn = connect_to_postgres()
            if postgres_conn:
                insert_item_data(postgres_conn, data)
                postgres_conn.close()
        except (Exception, psycopg2.Error) as error:
            print(f"Error inserting data: {error}")

    rabbitmq_channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback, auto_ack=True)

    try:
        print("Waiting for messages...")
        rabbitmq_channel.start_consuming()
    except KeyboardInterrupt:
        rabbitmq_channel.stop_consuming()
        rabbitmq_connection.close()

if __name__ == '__main__':
    main()

# import pika
# import json
# import configparser
# import psycopg2
# from psycopg2.extensions import register_adapter, AsIs
# from flask import Flask, render_template
#
# app = Flask(__name__)
#
# # Load configuration from a file (optional)
# config = configparser.ConfigParser()
# config.read('config.py')
# rabbitmq_host = config.get('rabbitmq', 'rabbitmq_host')  # Handle potential errors
# rabbitmq_port = config.get('rabbitmq', 'rabbitmq_port')  # Handle potential errors
# rabbitmq_user = config.get('rabbitmq', 'rabbitmq_user')  # Handle potential errors
# rabbitmq_password = config.get('rabbitmq', 'rabbitmq_password')  # Handle potential errors
# rabbitmq_queue = config.get('rabbitmq', 'rabbitmq_queue')  # Handle potential errors
#
#
# # PostgreSQL configuration
# db_config = {
#     "host": config.get('postgres', 'pg_host'),
#     "port": config.get('postgres', 'pg_port'),
#     "database": config.get('postgres', 'pg_database'),
#     "user": config.get('postgres', 'pg_user'),
#     "password": config.get('postgres', 'pg_password'),
# }
#
# def load_json_data(json_data, table_name, db_config):
#     """
#     Loads JSON data into a PostgreSQL table.
#
#     Args:
#         json_data (dict): The JSON data to load.
#         table_name (str): The name of the table.
#         db_config (dict): A dictionary containing database connection parameters.
#     """
#
#     with psycopg2.connect(**db_config) as conn:
#         with conn.cursor() as cur:
#             # Extract values from JSON data
#             make = json_data['make']
#             model = json_data['model']
#             gps_location = json_data['gps-location'].split(',')
#             owner_name = json_data['owner-name']
#             mileage = json_data['mileage']
#             fuel_level = json_data['fuel_level']
#             temperature = json_data['temperature']
#             serviced_date = json_data['serviced_date']
#             next_service_date = json_data['next_service_date']
#             vehicle_alerts = json_data['vehicle_alerts']
#
#             #latitude, longitude  = gps-location
#             # print(gps_location)
#             gps_location_str = ''.join(gps_location)
#             # print(gps_location_str)
#             latitude, longitude  = gps_location_str.split(' ')
#             # data_without_brackets = vehicle_alerts[1:-1]
#
#             # print(latitude,longitude)
#             lat = float(latitude)
#             lon = float(longitude)
#             # print(lat,lon)
#             # print(data_without_brackets)
#
#             # Insert data into the table
#             cur.execute(
#                 f"""
#                 INSERT INTO vehicles (make, model, latitude, longitude, ownername, mileage, fuel_level, temperature, serviced_date, next_service_date, vehicle_alerts)
#                 VALUES (%s, %s, %s::numeric, %s::numeric, %s, %s, %s, %s, %s, %s, %s)
#                 """,
#                 (make, model, lat, lon ,owner_name, mileage, fuel_level, temperature, serviced_date, next_service_date, vehicle_alerts)
#             )
#
#             # print(query % (make, model, latitude, longitude , mileage, fuel_level, temperature, serviced_date, next_service_date, vehicle_alerts))
#
#             conn.commit()
#             print("Data inserted successfully!")
#
# def consume_from_rabbitmq(queue_name):
#     credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
#     connection = pika.BlockingConnection(
#         pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
#     )
#     channel = connection.channel()
#
#     def callback(ch, method, properties, body):
#         json_data = json.loads(body)
#         # print(json.dumps(json_data, indent=4))
#         load_json_data(json_data, "vehicles", db_config)
#
#     channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
#
#     try:
#         channel.start_consuming()
#     except KeyboardInterrupt:
#         channel.stop_consuming()
#
#     connection.close()
#
# @app.route('/')
# def index():
#     return render_template('postgres.html')
#
# if __name__ == '__main__':
#     consume_from_rabbitmq(rabbitmq_queue)
#     app.run(debug=True, port=5004)

#
# CREATE TABLE vehicles (
#     id SERIAL PRIMARY KEY,
#     make VARCHAR(255) NOT NULL,
#     model VARCHAR(255) NOT NULL,
#     latitude VARCHAR(255) NOT NULL,
#     longitude VARCHAR(255) NOT NULL,
#     ownername VARCHAR(255) NOT NULL,
#     mileage INTEGER NOT NULL,
#     fuel_level VARCHAR(255) NOT NULL,
#     temperature VARCHAR(255) NOT NULL,
#     serviced_date DATE NOT NULL,
#     next_service_date DATE,
#     vehicle_alerts VARCHAR(255)[]
# );
