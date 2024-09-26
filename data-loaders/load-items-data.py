import pika
import json
import configparser
import psycopg2
import db_config

config = configparser.ConfigParser()
config.read('config.py')
rabbitmq_host = db_config.rabbitmq_host
rabbitmq_port = db_config.rabbitmq_port
rabbitmq_user = db_config.rabbitmq_user
rabbitmq_password = db_config.rabbitmq_password # Handle potential errors
items_data_queue = config.get('rabbitmq', 'items_data_queue')

def connect_to_rabbitmq(host='your_rabbitmq_host', queue_name=items_data_queue):
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

def insert_item_data(conn, item_data):
    """Inserts data into the items table."""

    cursor = conn.cursor()
    sql = """
        INSERT INTO items (type, name, description, availability, units_in_stock, cost, latitude, longitude, dealer_id, discount, promotion_code)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        item_data['type'],
        item_data['name'],
        item_data['description'],
        item_data['availability'],
        item_data['units_in_stock'],
        item_data['cost'],
        item_data['latitude'],
        item_data['longitude'],
        item_data['dealer_id'],
        item_data['discount'],
        item_data['promotion_code']
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
            insert_item_data(postgres_conn, data)
            postgres_conn.close()
        except (Exception, psycopg2.Error) as error:
            print(f"Error inserting data: {error}")

    rabbitmq_channel.basic_consume(queue=items_data_queue, on_message_callback=callback, auto_ack=True)

    try:
        print("Waiting for messages...")
        rabbitmq_channel.start_consuming()
    except KeyboardInterrupt:
        rabbitmq_channel.stop_consuming()
        rabbitmq_connection.close()

if __name__ == '__main__':
    main()
