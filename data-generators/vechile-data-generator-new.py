import json
import random
import time
import datetime
from geopy.distance import distance
from geopy.geocoders import Nominatim
import pika
import configparser
import db_config
from faker import Faker
from json import dumps


config = configparser.ConfigParser()
config.read('config.py')

rabbitmq_host = db_config.rabbitmq_host
rabbitmq_port = db_config.rabbitmq_port
rabbitmq_user = db_config.rabbitmq_user
rabbitmq_password = db_config.rabbitmq_password
rabbitmq_queue = config.get('rabbitmq', 'rabbitmq_queue')

def generate_random_car():
    fake = Faker()

    return {
        'make': fake.company(),
        'model': fake.word(),
        'gps-location': f'{random.uniform(11.7946, 80.7946)}, {random.uniform(-10.7946, -346.5348)}',
        #'gps-location': f'{fake.latitude()},{fake.longitude()}',  # Latitude,Longitude format
        'owner-name': fake.name(),
        'mileage': random.randint(0, 200000),
        'fuel_level': round(random.uniform(10, 70), 2),  # Percentage
        'temperature': round(random.uniform(-40, 125), 2),  # Celsius
        'serviced_date': fake.date_between(start_date='-10y', end_date='-1d').isoformat(),  # Past date within 1 year
        'next_service_date': fake.date_between(start_date='+1d', end_date='+5d').isoformat(),  # Future date within 1 year
                             # if random.random() < 0.1 else None),  # 10% chance of no next service date
        'vehicle_alerts': random.choices(['Engine Light On', 'Low Tire Pressure', 'Engine Temperature HOT', 'Oil Leak Found', 'Battery Needs replacements', 'Brakes failure', 'Gear Failure', 'Smoke Test Due', None], weights=[0.05, 0.1, 0.35, 0.02, 0.01, 0.005, 0.005, 0.005, 0.55])  # Random alerts
    }

# dumps(datetime.now(), default=json_serial)

# Connect to RabbitMQ
credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
)
channel = connection.channel()
channel.queue_declare(queue=rabbitmq_queue,durable=True,arguments={"x-queue-type": "quorum"})
# channel.queue_declare(queue=rabbitmq_queue)
# channel.queue_declare(queue='vehicle_data')

# Main loop to generate and send car data
for _ in range(1000):
    car_data = generate_random_car()
    channel.basic_publish(exchange='',
                         routing_key=rabbitmq_queue,
                         body=json.dumps(car_data))
    print("Sent:", json.dumps(car_data))

    time.sleep(1)  # Simulate sensor readings every minute

# Close the connection
connection.close()
