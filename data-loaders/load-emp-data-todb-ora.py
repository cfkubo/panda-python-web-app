import pika
import json
import configparser
import oracledb
import db_config


# Load configuration from a file (optional)
config = configparser.ConfigParser()
config.read('config.py')
rabbitmq_host = db_config.rabbitmq_host
rabbitmq_port = db_config.rabbitmq_port
rabbitmq_user = db_config.rabbitmq_user
rabbitmq_password = db_config.rabbitmq_password # Handle potential errors
employee_data_queue = config.get('rabbitmq', 'employee_data_queue')  # Handle potential errors

def connect_to_rabbitmq(host='your_rabbitmq_host', queue_name=employee_data_queue):
    """Establishes a connection to RabbitMQ."""

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
    )
    channel = connection.channel()
    # channel.queue_declare(queue=queue_name)
    return channel, connection

# def connect_to_postgres(host='127.0.0.1', db_name='postgres', user='arul', password='pass'):
#     """Establishes a connection to PostgreSQL."""
#
#     connection = oracledb.connect(
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
        connection = oracledb.connect(user=db_config.user, password=db_config.pw, dsn=db_config.dsn)

        return connection
    except (Exception, oracledb.Error) as error:
        print(f"Error connecting to PostgreSQL: {error}")
        return None  # Indicate connection failure

def insert_data_to_postgres(conn, employee_data):
    """Inserts data into the employees table."""

    cursor = conn.cursor()
    sql = """
        INSERT INTO employees (name, email, phone, role, department, hire_date, salary)
        VALUES (:name, :email, :phone, :role, :department, TO_DATE(:hire_date, 'YYYY-MM-DD'), :salary)
    """
    cursor.execute(sql, (
        employee_data['name'],
        employee_data['email'],
        employee_data['phone'],
        employee_data['role'],
        employee_data['department'],
        employee_data['hire_date'],
        employee_data['salary']
    ))
    conn.commit()
    cursor.close()
    print(f"Inserted employee data: {employee_data}")

def main():
    """Main function that connects to RabbitMQ and PostgreSQL, processes data, and inserts it into the table."""

    rabbitmq_channel, rabbitmq_connection = connect_to_rabbitmq()

    def callback(ch, method, properties, body):
        data = json.loads(body)
        try:
            postgres_conn = connect_to_postgres()
            insert_data_to_postgres(postgres_conn, data)
            postgres_conn.close()
        except (Exception, oracledb.Error) as error:
            print(f"Error inserting data: {error}")

    rabbitmq_channel.basic_consume(queue=employee_data_queue, on_message_callback=callback, auto_ack=True)

    try:
        print("Waiting for messages...")
        rabbitmq_channel.start_consuming()
    except KeyboardInterrupt:
        rabbitmq_channel.stop_consuming()
        rabbitmq_connection.close()

if __name__ == '__main__':
    main()
