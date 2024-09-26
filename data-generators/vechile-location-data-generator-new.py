import json
import random
import time
import datetime
from geopy.distance import distance
from geopy.geocoders import Nominatim
import pika
import configparser
from faker import Faker
from json import dumps
import random
import math
from datetime import datetime

config = configparser.ConfigParser()
config.read('config.py')

rabbitmq_host = config.get('rabbitmq', 'rabbitmq_host')
rabbitmq_port = config.get('rabbitmq', 'rabbitmq_port')
rabbitmq_user = config.get('rabbitmq', 'rabbitmq_user')
rabbitmq_password = config.get('rabbitmq', 'rabbitmq_password')
vechicle_location_queue_live = config.get('rabbitmq', 'vechicle_location_queue_live')

def interpolate_points(start, end, steps):
    """Interpolate points between start and end with a given number of steps."""
    latitudes = [start[0] + i * (end[0] - start[0]) / (steps - 1) for i in range(steps)]
    longitudes = [start[1] + i * (end[1] - start[1]) / (steps - 1) for i in range(steps)]
    return list(zip(latitudes, longitudes))

def simulate_movement(start, end, steps):
    """Simulate car movement from start to end."""
    points = interpolate_points(start, end, steps)
    # Add a bit of randomness to simulate real-world movement
    noisy_points = [(lat + random.uniform(-0.001, 0.001), lon + random.uniform(-0.001, 0.001)) for lat, lon in points]
    return noisy_points

def generate_random_car():
    fake = Faker()
    # Define start and end coordinates
    start_coordinate = (40.7128, -74.0060)  # Example: New York City
    end_coordinate = (34.0522, -118.2437)    # Example: Los Angeles

    # Number of steps or intermediate points
    num_steps = 10

    # Generate and print the simulated GPS coordinates
    path = simulate_movement(start_coordinate, end_coordinate, num_steps)

    print("Simulated GPS Coordinates:")
    for idx, (latitude, longitude) in enumerate(path):
        # print(f"Step {idx + 1}: Latitude = {latitude}, Longitude = {longitude}")

        return {
            "vehicle_id": random.randint(1, 1),
            'timestamp': datetime.now().isoformat(),
            # 'gps-location': f'{latitude},{longitude}',
            'latitude': f'{latitude}',
            'longitude': f'{longitude}',
            # 'gps-location': f'{random.uniform(11.7946, 80.7946)}, {random.uniform(-10.7946, -346.5348)}',
            #'gps-location': f'{fake.latitude()},{fake.longitude()}',  # Latitude,Longitude format
            "speed": random.randint(60, 100),
            'mileage': random.randint(100,100000),
            "fuel_level": random.randint(0, 100),
            'temperature': random.randint(0,100),
            "battery_level": random.uniform(0,100),
            "engine_status": random.choice([True, False]),
            'next_service_date': fake.date_between(start_date='+1d', end_date='+5d').isoformat(),
            'vehicle_alerts': random.choices(['Engine Light On', 'Low Tire Pressure', 'Engine Temperature HOT', 'Oil Leak Found', 'Battery Needs replacements', 'Brakes failure', 'Gear Failure', 'Smoke Test Due', None], weights=[0.05, 0.1, 0.35, 0.02, 0.01, 0.005, 0.005, 0.005, 0.55])  # Random alerts
        }

# dumps(datetime.now(), default=json_serial)

# Connect to RabbitMQ
credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
)
channel = connection.channel()
channel.queue_declare(queue=vechicle_location_queue_live,durable=True,arguments={"x-queue-type": "quorum"})
# channel.queue_declare(queue=vechicle_location_queue_live)
# channel.queue_declare(queue='vehicle_data')

# Main loop to generate and send car data
for _ in range(1000):
    car_data = generate_random_car()
    channel.basic_publish(exchange='',
                         routing_key=vechicle_location_queue_live,
                         body=json.dumps(car_data))
    print("Sent:", json.dumps(car_data))

    time.sleep(1)  # Simulate sensor readings every minute

# Close the connection
connection.close()
