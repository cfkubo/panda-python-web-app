import pika
import json
import random
import faker
from datetime import datetime
import configparser
import time

config = configparser.ConfigParser()
config.read('config.py')

rabbitmq_host = config.get('rabbitmq', 'rabbitmq_host')
rabbitmq_port = config.get('rabbitmq', 'rabbitmq_port')
rabbitmq_user = config.get('rabbitmq', 'rabbitmq_user')
rabbitmq_password = config.get('rabbitmq', 'rabbitmq_password')
vechicle_location_queue = config.get('rabbitmq', 'vechicle_location_queue')

def generate_random_vehicle_location_data():
    """Generates random data for a vehicle location."""

    fake = faker.Faker()
    data = {
        "vehicle_id": random.randint(1, 100),  # Assuming 'vehicles' table has IDs
        "timestamp": datetime.now().isoformat(),
        "location": f"POINT({random.uniform(-180, 180)} {random.uniform(-90, 90)})",
        "speed": random.randint(60, 100),
        "direction": random.randint(0, 360),
        "battery_level": random.uniform(0, 100),
        "engine_status": random.choice([True, False]),
        "alerts": [random.choice(["Low Battery", "Engine Overheat", "Tire Pressure Low"])]
    }
    return data

def send_to_rabbitmq(queue_name, data):
    """Sends JSON data to a RabbitMQ queue."""

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
    )
    channel = connection.channel()
    channel.queue_declare(queue=vechicle_location_queue,durable=True,arguments={"x-queue-type": "quorum"})
    # Main loop to generate and send car data
    while True:
        vehicle_location_data = generate_random_vehicle_location_data()
        channel.basic_publish(exchange='',
                             routing_key=vechicle_location_queue,
                             body=json.dumps(vehicle_location_data))
        print("Sent:", json.dumps(vehicle_location_data))

        time.sleep(1)  # Simulate sensor readings every minute
    print("Data sent to RabbitMQ")

    connection.close()

if __name__ == "__main__":
    # queue_name = "vehicle_locations_queue"  # Replace with your desired queue name

    for _ in range(1000):  # Generate 10 random vehicle locations
        vehicle_location_data = generate_random_vehicle_location_data()
        send_to_rabbitmq(vechicle_location_queue, vehicle_location_data)
        print("Sent:", json.dumps(vehicle_location_data))
