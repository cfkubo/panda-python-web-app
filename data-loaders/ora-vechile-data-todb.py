import pika
import json
import oracledb
import configparser
import db_config
import db_config

config = configparser.ConfigParser()
config.read('config.py')

# db_config = {
#     "oracle_host": config.get('oracle', 'oracle_host'),
#     "oracle_port": config.get('oracle', 'oracle_port'),
#     "oracle_database": config.get('oracle', 'oracle_database'),
#     "oracle_user": config.get('oracle', 'oracle_user'),
#     "oracle_password": config.get('oracle', 'oracle_password'),
# }

rabbitmq_host = db_config.rabbitmq_host
rabbitmq_port = db_config.rabbitmq_port
rabbitmq_user = db_config.rabbitmq_user
rabbitmq_password = db_config.rabbitmq_password
rabbitmq_queue = config.get('rabbitmq', 'rabbitmq_queue')

def connect_to_rabbitmq(host=rabbitmq_host, queue_name=rabbitmq_queue):
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
    )
    channel = connection.channel()
    return channel, connection

def consume_messages():
    channel, connection = connect_to_rabbitmq()

    def callback(ch, method, properties, body):
        data = json.loads(body)
        insert_vehicle_data(data)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()

    connection.close()

def insert_vehicle_data(data):
    # CONN_STR = '{oracle_user}/{oracle_password}@{oracle_host}:{oracle_port}/{oracle_database}'.format(**db_config)
    CONN_STR = oracledb.connect(user=db_config.user, password=db_config.pw, dsn=db_config.dsn)


    # dsn_tns = oracledb.makedsn(db_config['host'], db_config['port'], db_config['database'])
    with oracledb.connect(user=db_config.user, password=db_config.pw, dsn=db_config.dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO  vehicles (make, model, latitude, longitude, ownername, mileage, fuel_level, temperature, serviced_date, next_service_date, vehicle_alerts)
                VALUES (:make, :model, :latitude, :longitude, :ownername, :mileage, CAST(:fuel_level AS NUMBER), :temperature, TO_DATE(:serviced_date, 'YYYY-MM-DD'), TO_DATE(:next_service_date, 'YYYY-MM-DD'), :vehicle_alerts)
            """, (
                data['make'],
                data['model'],
                data['gps-location'].split(',')[0],
                data['gps-location'].split(',')[1],
                data['ownername'],
                data['mileage'],
                data['fuel_level'],
                data['temperature'],
                data['serviced_date'],
                data['next_service_date'],
                json.dumps(data['vehicle_alerts'])
            ))
            conn.commit()

if __name__ == "__main__":
    consume_messages()
