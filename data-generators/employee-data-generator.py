import pika
import json
import random
import faker
import configparser
import db_config

config = configparser.ConfigParser()
config.read('config.py')

rabbitmq_host = db_config.rabbitmq_host
rabbitmq_port = db_config.rabbitmq_port
rabbitmq_user = db_config.rabbitmq_user
rabbitmq_password = db_config.rabbitmq_password
employee_data_queue = config.get('rabbitmq', 'employee_data_queue')

def generate_random_employee_data():
    """Generates random data for an employee."""

    fake = faker.Faker()
    data = {
        "name": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "role": fake.job(),
        "department": fake.company(),
        "hire_date": fake.date_object().strftime('%Y-%m-%d'),  # Format date as YYYY-MM-DD
        "salary": round(random.uniform(30000, 100000), 2)
    }
    return data

def send_to_rabbitmq(employee_data_queue, data):
    """Sends JSON data to a RabbitMQ queue."""

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
    )
    channel = connection.channel()
    channel.queue_declare(queue=employee_data_queue,durable=True,arguments={"x-queue-type": "quorum"})
    channel.basic_publish(exchange='', routing_key=employee_data_queue, body=json.dumps(data))
    print("Data sent to RabbitMQ")

    connection.close()

if __name__ == "__main__":
    # employee_data_queue = "employees_queue"  # Replace with your desired queue name

    for _ in range(1000):  # Generate 10 random employees
        employee_data = generate_random_employee_data()
        send_to_rabbitmq(employee_data_queue, employee_data)
        print("Sent:", json.dumps(employee_data))
