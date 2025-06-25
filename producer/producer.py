import json
import time
import random
import socket
import logging
from kafka import KafkaProducer
from faker import Faker

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def wait_for_kafka(host, port, retry_interval=3):
    """Aguarda o Kafka estar disponível."""
    while True:
        try:
            with socket.create_connection(address=(host, port), timeout=5):
                logging.info("Kafka disponível!")
                break
        except Exception as e:
            logging.warning(f"Aguardando Kafka... ({e})")
            time.sleep(retry_interval)

def create_kafka_producer():
    """Cria e retorna um KafkaProducer."""
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers='kafka:9092',
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            logging.info("KafkaProducer conectado!")
            return producer
        except Exception as e:
            logging.warning(f"Aguardando KafkaProducer... ({e})")
            time.sleep(3)

def generate_sensor_data(fake):
    """Gera dados simulados de sensores."""
    return {
        "sensor_id": fake.uuid4(),
        "location": fake.city(),
        "temperature": round(random.uniform(20.0, 40.0), 2),
        "humidity": round(random.uniform(30.0, 90.0), 2),
        "timestamp": fake.iso8601()
    }

def main(): # pragma no cover
    fake = Faker()
    wait_for_kafka('kafka', 9092)
    producer = create_kafka_producer()

    while True:
        data = generate_sensor_data(fake)
        logging.info(f"Produzindo: {data}")
        producer.send('iot_sensors', value=data)
        time.sleep(60)

if __name__ == "__main__": # pragma no cover
    main()