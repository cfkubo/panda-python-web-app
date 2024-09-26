import pika
import json
import random
import faker
import configparser
import db_config

# Load configuration from a file (optional)
config = configparser.ConfigParser()
config.read('config.py')

rabbitmq_host = db_config.rabbitmq_host
rabbitmq_port = db_config.rabbitmq_port
rabbitmq_user = db_config.rabbitmq_user
rabbitmq_password = db_config.rabbitmq_password # Handle potential errors
rabbitmq_queue = config.get('rabbitmq', 'rabbitmq_queue')  # Handle potential errors

def generate_random_car_model_data():
    """Generates random data for a car model."""

    fake = faker.Faker()
    data = {
        "name": fake.company(),
        "model": fake.word(),
        "generations": random.randint(1, 10),
        "sold_units": random.randint(1000, 100000),
        "in_stock_units": random.randint(0, 1000),
        "damaged_units": random.randint(0, 50),
        "manufacturer": fake.company(),
        "year_first_released": random.randint(1900, 2024),
        "body_type": random.choice(["Sedan", "SUV", "Coupe", "Hatchback", "Truck", "Van"]),
        "engine_type": random.choice(["Gasoline", "Diesel", "Electric", "Hybrid"]),
        "fuel_type": random.choice(["Gasoline", "Diesel", "Electric"]),
        "transmission_type": random.choice(["Manual", "Automatic", "CVT"]),
        "price_range": random.randint(10000, 100000),
        "safety_rating": random.choice(["5-star", "4-star", "3-star", "2-star", "1-star"]),
        "features": fake.text(max_nb_chars=200)
    }
    return data

def send_to_rabbitmq(car_models_queue, data):
    """Sends JSON data to a RabbitMQ queue."""

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
    )

    channel = connection.channel()
    channel.queue_declare(queue=car_models_queue,durable=True,arguments={"x-queue-type": "quorum"})
    channel.basic_publish(exchange='',
                         routing_key=car_models_queue,
                         body=json.dumps(car_model_data))
    #print("Sent:", json.dumps(car_model_data))

    return channel, connection


if __name__ == "__main__":
    car_models_queue = "car_models_queue"  # Replace with your desired queue name

    for _ in range(1000):  # Generate 10 random car models
        car_model_data = generate_random_car_model_data()
        send_to_rabbitmq(car_models_queue, car_model_data)
        print("Sent:", json.dumps(car_model_data))
