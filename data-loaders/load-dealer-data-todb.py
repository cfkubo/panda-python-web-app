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
dealer_data_queue = config.get('rabbitmq', 'dealer_data_queue')

def connect_to_rabbitmq(host='your_rabbitmq_host', queue_name=dealer_data_queue):
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


def insert_dealer_data(conn, dealer_data):
    """Inserts data into the dealers table."""

    cursor = conn.cursor()
    sql = """
        INSERT INTO dealers (name, address, city, state, country, contact_name, contact_email, contact_phone, website)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        dealer_data['name'],
        dealer_data['address'],
        dealer_data['city'],
        dealer_data['state'],
        dealer_data['country'],
        dealer_data['contact_name'],
        dealer_data['contact_email'],
        dealer_data['contact_phone'],
        dealer_data['website']
    ))
    conn.commit()
    cursor.close()
    print(f"Inserted dealer data: {dealer_data}")

def main():
    """Main function that connects to RabbitMQ and PostgreSQL, processes data, and inserts it into the table."""

    rabbitmq_channel, rabbitmq_connection = connect_to_rabbitmq()

    def callback(ch, method, properties, body):
        data = json.loads(body)
        try:
            postgres_conn = connect_to_postgres()
            insert_dealer_data(postgres_conn, data)
            postgres_conn.close()
        except (Exception, psycopg2.Error) as error:
            print(f"Error inserting data: {error}")

    rabbitmq_channel.basic_consume(queue=dealer_data_queue, on_message_callback=callback, auto_ack=True)

    try:
        print("Waiting for messages...")
        rabbitmq_channel.start_consuming()
    except KeyboardInterrupt:
        rabbitmq_channel.stop_consuming()
        rabbitmq_connection.close()

if __name__ == '__main__':
    main()
