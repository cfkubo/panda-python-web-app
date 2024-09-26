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
dealer_data_queue = config.get('rabbitmq', 'dealer_data_queue')

def generate_random_dealer_data():
    """Generates random data for a dealer."""

    fake = faker.Faker()
    data = {
        "name": fake.company(),
        "address": fake.street_address(),
        "city": fake.city(),
        "state": fake.state(),
        "country": "USA",  # You can adjust the country as needed
        "contact_name": fake.name(),
        "contact_email": fake.email(),
        "contact_phone": fake.phone_number(),
        "website": fake.url()
    }
    return data

def send_to_rabbitmq(dealer_data_queue, data):
    """Sends JSON data to a RabbitMQ queue."""

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
    )
    channel = connection.channel()
    channel.queue_declare(queue=dealer_data_queue,durable=True,arguments={"x-queue-type": "quorum"})

    channel.basic_publish(exchange='', routing_key=dealer_data_queue, body=json.dumps(data))
    print("Data sent to RabbitMQ")

    connection.close()

if __name__ == "__main__":
    # dealer_data_queue = "dealers_queue"  # Replace with your desired queue name

    for _ in range(1000):  # Generate 10 random dealers
        dealer_data = generate_random_dealer_data()
        send_to_rabbitmq(dealer_data_queue, dealer_data)
        print("Sent:", json.dumps(dealer_data))
