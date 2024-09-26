import pika
import json
import psycopg2
import configparser
import db_config

config = configparser.ConfigParser()
config.read('config.py')

# RabbitMQ configuration
rabbitmq_host = db_config.rabbitmq_host
rabbitmq_port = db_config.rabbitmq_port
rabbitmq_user = db_config.rabbitmq_user
rabbitmq_password = db_config.rabbitmq_password
rabbitmq_owner_queue = config.get('rabbitmq', 'rabbitmq_owner_queue')

# PostgreSQL configuration (moved to config section)
# pg_host = db_config.pg_host
# pg_database = db_config.pg_database
# pg_user = db_config.pg_user
# pg_password = db_config.pg_password



def connect_to_rabbitmq(rabbitmq_owner_queue):
    """Establishes a connection to RabbitMQ."""

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
    )

    channel = connection.channel()
    # channel.queue_declare(queue=rabbitmq_owner_queue)
    return channel, connection


def connect_to_postgres():
    """Establishes a connection to PostgreSQL using configuration."""

    try:
        connection = psycopg2.connect(host=db_config.pg_host, password=db_config.pg_password, database=db_config.pg_database, user=db_config.pg_user, port=db_config.pg_port)
        return connection
    except (Exception, psycopg2.Error) as error:
        print(f"Error connecting to PostgreSQL: {error}")
        return None  # Indicate connection failure


def process_owner_data(data):
    """Preprocesses owner data, removing potential newline characters in the address."""

    return {
        "name": data["name"],
        "email": data["email"],
        "phone": data["phone"].strip(),  # Remove potential leading/trailing whitespace
        "address": data["address"].strip().replace("\n", " ")  # Remove newline and replace with space
    }


def insert_data_to_postgres(conn, owner_data):
    """Inserts data into the owners table."""

    cursor = conn.cursor()
    sql = """
        INSERT INTO owners (name, email, phone, address)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (owner_data["name"], owner_data["email"], owner_data["phone"], owner_data["address"]))
    conn.commit()
    cursor.close()
    print(f"Inserted owner data: {owner_data}")


def main():
    """Main function that connects to RabbitMQ and PostgreSQL, processes data, and inserts it into the table."""

    rabbitmq_channel, rabbitmq_connection = connect_to_rabbitmq(rabbitmq_owner_queue)

    def callback(ch, method, properties, body):
        data = json.loads(body)
        processed_data = process_owner_data(data)

        postgres_conn = connect_to_postgres()  # Connect to PostgreSQL using configuration
        if postgres_conn:
            try:
                insert_data_to_postgres(postgres_conn, processed_data)
            except (Exception, psycopg2.Error) as error:
                print(f"Error inserting data: {error}")
            finally:
                postgres_conn.close()  # Close connection in any case (success or error)

    rabbitmq_channel.basic_consume(queue=rabbitmq_owner_queue, on_message_callback=callback, auto_ack=True)

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
# import psycopg2
# import configparser
#
# config = configparser.ConfigParser()
# config.read('config.py')
#
# rabbitmq_host = config.get('rabbitmq', 'rabbitmq_host')
# rabbitmq_port = config.get('rabbitmq', 'rabbitmq_port')
# rabbitmq_user = config.get('rabbitmq', 'rabbitmq_user')
# rabbitmq_password = config.get('rabbitmq', 'rabbitmq_password')
# rabbitmq_owner_queue = config.get('rabbitmq', 'rabbitmq_owner_queue')
#
#
# def connect_to_rabbitmq(rabbitmq_owner_queue):
#     """Establishes a connection to RabbitMQ."""
#
#     credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
#     connection = pika.BlockingConnection(
#         pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
#     )
#
#     channel = connection.channel()
#     # channel.queue_declare(queue=rabbitmq_owner_queue)
#     return channel, connection
#
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
#
# def process_owner_data(data):
#     """Preprocesses owner data, removing potential newline characters in the address."""
#
#     return {
#         "name": data["name"],
#         "email": data["email"],
#         "phone": data["phone"].strip(),  # Remove potential leading/trailing whitespace
#         "address": data["address"].strip().replace("\n", " ")  # Remove newline and replace with space
#     }
#
# def insert_data_to_postgres(conn, owner_data):
#     """Inserts data into the owners table."""
#
#     cursor = conn.cursor()
#     sql = """
#         INSERT INTO owners (name, email, phone, address)
#         VALUES (%s, %s, %s, %s)
#     """
#     cursor.execute(sql, (owner_data["name"], owner_data["email"], owner_data["phone"], owner_data["address"]))
#     conn.commit()
#     cursor.close()
#     print(f"Inserted owner data: {owner_data}")
#
# def main():
#     """Main function that connects to RabbitMQ and PostgreSQL, processes data, and inserts it into the table."""
#
#     rabbitmq_channel, rabbitmq_connection = connect_to_rabbitmq(rabbitmq_owner_queue)
#
#     def callback(ch, method, properties, body):
#         data = json.loads(body)
#         processed_data = process_owner_data(data)
#         try:
#             postgres_conn = connect_to_postgres()
#             insert_data_to_postgres(postgres_conn, processed_data)
#             postgres_conn.close()
#         except (Exception, psycopg2.Error) as error:
#             print(f"Error inserting data: {error}")
#
#     rabbitmq_channel.basic_consume(queue=rabbitmq_owner_queue, on_message_callback=callback, auto_ack=True)
#
#     try:
#         print("Waiting for messages...")
#         rabbitmq_channel.start_consuming()
#     except KeyboardInterrupt:
#         rabbitmq_channel.stop_consuming()
#         rabbitmq_connection.close()
#
# if __name__ == '__main__':
#     main()


#  CREATE TABLE owners (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(255) NOT NULL,
#     email VARCHAR(255) UNIQUE NOT NULL,
#     phone VARCHAR(40),
#     address TEXT
# );
