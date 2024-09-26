import pika
import json
import configparser
import psycopg2
import db_config

# Load configuration from a file (optional)
config = configparser.ConfigParser()
config.read('config.py')

rabbitmq_host = db_config.rabbitmq_host
rabbitmq_port = db_config.rabbitmq_port
rabbitmq_user = db_config.rabbitmq_user
rabbitmq_password = db_config.rabbitmq_password# Handle potential errors
car_models_queue = config.get('rabbitmq', 'car_models_queue')  # Handle potential errors

def connect_to_rabbitmq(host='your_rabbitmq_host', queue_name='car_models_queue'):
    """Establishes a connection to RabbitMQ."""

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
    )
    channel = connection.channel()
    return channel, connection

# def connect_to_postgres(host='127.0.0.1', db_name='postgres', user='arul', password='pass'):
#     """Establishes a connection to PostgreSQL."""
#
#     connection = psycopg2.connect(
#         host=host,
#         database=db_name,
#         user=user,
#         password=password
#     )
#     return connection

def connect_to_postgres():
    """Establishes a connection to PostgreSQL using configuration."""

    try:
        # Access configuration values
        pg_host = db_config.pg_host
        pg_database = db_config.pg_database
        pg_user = db_config.pg_user
        pg_password = db_config.pg_password

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

def insert_data_to_postgres(conn, car_model_data):
    """Inserts data into the car_models table."""

    cursor = conn.cursor()
    sql = """
        INSERT INTO car_models (name, model, generations, sold_units, in_stock_units, damaged_units, manufacturer, year_first_released, body_type, engine_type, fuel_type, transmission_type, price_range, safety_rating, features)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        car_model_data['name'],
        car_model_data['model'],
        car_model_data['generations'],
        car_model_data['sold_units'],
        car_model_data['in_stock_units'],
        car_model_data['damaged_units'],
        car_model_data['manufacturer'],
        car_model_data['year_first_released'],
        car_model_data['body_type'],
        car_model_data['engine_type'],
        car_model_data['fuel_type'],
        car_model_data['transmission_type'],
        car_model_data['price_range'],
        car_model_data['safety_rating'],
        json.dumps(car_model_data['features'])  # Convert features to JSON string
    ))
    conn.commit()
    cursor.close()
    print(f"Inserted car model data: {car_model_data}")

def main():
    """Main function that connects to RabbitMQ and PostgreSQL, processes data, and inserts it into the table."""

    rabbitmq_channel, rabbitmq_connection = connect_to_rabbitmq()

    def callback(ch, method, properties, body):
        data = json.loads(body)
        try:
            postgres_conn = connect_to_postgres()
            insert_data_to_postgres(postgres_conn, data)
            postgres_conn.close()
        except (Exception, psycopg2.Error) as error:
            print(f"Error inserting data: {error}")

    rabbitmq_channel.basic_consume(queue='car_models_queue', on_message_callback=callback, auto_ack=True)

    try:
        print("Waiting for messages...")
        rabbitmq_channel.start_consuming()
    except KeyboardInterrupt:
        rabbitmq_channel.stop_consuming()
        rabbitmq_connection.close()

if __name__ == '__main__':
    main()


# CREATE TABLE car_models (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(255) NOT NULL,
#     model VARCHAR(255) NOT NULL,
#     generations INTEGER,
#     sold_units INTEGER,
#     in_stock_units INTEGER,
#     damaged_units INTEGER,
#     manufacturer VARCHAR(255),
#     year_first_released INTEGER,
#     body_type VARCHAR(255),
#     engine_type VARCHAR(255),
#     fuel_type VARCHAR(255),
#     transmission_type VARCHAR(255),
#     price_range NUMERIC,
#     safety_rating VARCHAR(255),
#     features TEXT  -- Store additional features as JSON or text
# );
