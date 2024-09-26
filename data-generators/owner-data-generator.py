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
rabbitmq_owner_queue = config.get('rabbitmq', 'rabbitmq_owner_queue')

def generate_random_owner_data():
    """Generates random data for an owner."""

    fake = faker.Faker()
    data = {
        "name": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "address": fake.address()
    }
    return data

def send_to_rabbitmq(queue_name, data):
    """Sends JSON data to a RabbitMQ queue."""

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
    )
    channel = connection.channel()
    channel.queue_declare(queue=rabbitmq_owner_queue,durable=True,arguments={"x-queue-type": "quorum"})

    channel.basic_publish(exchange='', routing_key=rabbitmq_owner_queue, body=json.dumps(data))
    print("Sent:", json.dumps(data))

    connection.close()

if __name__ == "__main__":
    # queue_name = "owners_queue"  # Replace with your desired queue name

    for _ in range(1000):  # Generate 10 random owners
        owner_data = generate_random_owner_data()
        send_to_rabbitmq(rabbitmq_owner_queue, owner_data)
