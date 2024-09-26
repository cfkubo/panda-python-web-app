import pika
import json
import random
import faker
from datetime import datetime
import configparser
import db_config

config = configparser.ConfigParser()
config.read('config.py')

rabbitmq_host = db_config.rabbitmq_host
rabbitmq_port = db_config.rabbitmq_port
rabbitmq_user = db_config.rabbitmq_user
rabbitmq_password = db_config.rabbitmq_password
items_data_queue = config.get('rabbitmq', 'items_data_queue')


def generate_random_item_data():
    """Generates random data for an item."""

    fake = faker.Faker()
    data = {
        "type": random.choice(["car", "airplane", "drone", "boat", "motorcycle", "robot", "plants" , "gold", "silver" , "bitcoin"]),
        "name": fake.company(),
        "description": fake.text(max_nb_chars=200),
        "availability": random.choice([True, False]),
        "units_in_stock": random.randint(0, 100),
        "cost": round(random.uniform(100, 10000), 2),
        "latitude": round(random.uniform(-90, 90), 6),
        "longitude": round(random.uniform(-180, 180), 6),
        "dealer_id": random.randint(1, 100),  # Assuming a 'dealers' table exists
        "discount": round(random.uniform(0, 30), 2),
        "promotion_code": random.choice(["SUMMER23", "WINTERSALE", "FREESHIP", "VIP10"])
    }
    return data

def send_to_rabbitmq(items_data_queue, data):
    """Sends JSON data to a RabbitMQ queue."""

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
    )
    channel = connection.channel()
    channel.queue_declare(queue=items_data_queue,durable=True,arguments={"x-queue-type": "quorum"})
    channel.basic_publish(exchange='', routing_key=items_data_queue, body=json.dumps(data))
    print("Data sent to RabbitMQ")

    connection.close()

if __name__ == "__main__":
    # items_data_queue = "items_queue"  # Replace with your desired queue name

    for _ in range(1000):  # Generate 10 random items
        item_data = generate_random_item_data()
        send_to_rabbitmq(items_data_queue, item_data)
        print("Sent:", json.dumps(item_data))
