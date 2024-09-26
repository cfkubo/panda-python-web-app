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
rabbitmq_password = db_config.rabbitmq_password # Handle potential errors
car_sales_queue = config.get('rabbitmq', 'car_sales_queue')

def generate_random_car_sale_data():
    """Generates random data for a car sale."""

    fake = faker.Faker()
    data = {
        "model_id": random.randint(1, 1000),  # Assuming 'car_models' table has IDs
        "color": fake.random_element(["Red", "Blue", "Black", "White", "Silver"]),
        "vin_number": fake.vin(),
        # fake.unique_random_element(elements=[fake.unique_random_number(digits=17) for _ in range(100)]),
        "sold_date": datetime.now().strftime("%Y-%m-%d"),
        "latitude": round(random.uniform(-90, 90), 6),
        "longitude": round(random.uniform(-180, 180), 6),
        "dealer_name": fake.company(),
        "list_price": round(random.uniform(15000, 50000), 2),
        "sale_price": round(random.uniform(12000, 45000), 2),
        "on_loan": random.choice([True, False]),
        "paid_cash": random.choice([True, False]),
        "customer_name": fake.name(),
        "customer_email": fake.email(),
        "customer_phone": fake.phone_number(),
        "salesperson_id": random.randint(1, 50)  # Assuming 'employees' table has IDs
    }
    return data

def send_to_rabbitmq(car_sales_queue, data):
    """Sends JSON data to a RabbitMQ queue."""

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
    )

    channel = connection.channel()
    channel.queue_declare(queue=car_sales_queue,durable=True,arguments={"x-queue-type": "quorum"})

    channel.basic_publish(exchange='', routing_key=car_sales_queue, body=json.dumps(data))
    print("Data sent to RabbitMQ")

    connection.close()

if __name__ == "__main__":
    car_sales_queue = "car_sales_queue"  # Replace with your desired queue name

    for _ in range(1000):  # Generate 10 random car sales
        car_sale_data = generate_random_car_sale_data()
        send_to_rabbitmq(car_sales_queue, car_sale_data)
        print("Sent:", json.dumps(car_sale_data))
