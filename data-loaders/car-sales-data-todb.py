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
car_sales_queue = config.get('rabbitmq', 'car_sales_queue')

# pg_host = config.get('postgres', 'pg_host')  # Handle potential errors
# pg_port = config.get('postgres', 'pg_port')  # Handle potential errors
# pg_user = config.get('postgres', 'pg_user')  # Handle potential errors
# pg_password = config.get('postgres', 'pg_password')  # Handle potential errors
# pg_database = config.get('postgres', 'pg_database')



def connect_to_rabbitmq(host='your_rabbitmq_host', queue_name=car_sales_queue):
    """Establishes a connection to RabbitMQ."""

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
    )
    channel = connection.channel()
    return channel, connection

# def connect_to_postgres(host=pg_host, db_name=pg_database, user=pg_user, password=pg_password):
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

def insert_car_sale_data(conn, car_sale_data):
    """Inserts data into the car_sales table."""

    cursor = conn.cursor()
    sql = """
        INSERT INTO car_sales (model_id, color, vin_number, sold_date, latitude, longitude, dealer_name, list_price, sale_price, on_loan, paid_cash, customer_name, customer_email, customer_phone, salesperson_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        car_sale_data['model_id'],
        car_sale_data['color'],
        car_sale_data['vin_number'],
        car_sale_data['sold_date'],
        car_sale_data['latitude'],
        car_sale_data['longitude'],
        car_sale_data['dealer_name'],
        car_sale_data['list_price'],
        car_sale_data['sale_price'],
        car_sale_data['on_loan'],
        car_sale_data['paid_cash'],
        car_sale_data['customer_name'],
        car_sale_data['customer_email'],
        car_sale_data['customer_phone'],
        car_sale_data['salesperson_id']
    ))
    conn.commit()
    cursor.close()
    print(f"Inserted car sale data: {car_sale_data}")

def main():
    """Main function that connects to RabbitMQ and PostgreSQL, processes data, and inserts it into the table."""

    rabbitmq_channel, rabbitmq_connection = connect_to_rabbitmq()

    def callback(ch, method, properties, body):
        data = json.loads(body)
        try:
            postgres_conn = connect_to_postgres()
            insert_car_sale_data(postgres_conn, data)
            postgres_conn.close()
        except (Exception, psycopg2.Error) as error:
            print(f"Error inserting data: {error}")

    rabbitmq_channel.basic_consume(queue=car_sales_queue, on_message_callback=callback, auto_ack=True)

    try:
        print("Waiting for messages...")
        rabbitmq_channel.start_consuming()
    except KeyboardInterrupt:
        rabbitmq_channel.stop_consuming()
        rabbitmq_connection.close()

if __name__ == '__main__':
    main()
