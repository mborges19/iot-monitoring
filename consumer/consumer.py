import json
import time
import socket
import logging

from kafka import KafkaConsumer
from sqlalchemy import create_engine, Table, Column, String, Float, MetaData
from sqlalchemy.exc import OperationalError

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def wait_for_postgres(engine, retry_interval=3):
    """Aguarda o PostgreSQL estar disponível."""
    while True:
        try:
            with engine.connect():
                logging.info("PostgreSQL disponível!")
                break
        except OperationalError:
            logging.warning("Aguardando PostgreSQL...")
            time.sleep(retry_interval)

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

def get_engine():
    """Cria a engine de conexão com o PostgreSQL."""
    return create_engine("postgresql://admin:admiot@postgres:5432/iotdb")

def create_sensors_table(metadata):
    """Define a tabela de sensores."""
    return Table(
        'sensors', metadata,
        Column('sensor_id', String),
        Column('location', String),
        Column('temperature', Float),
        Column('humidity', Float),
        Column('timestamp', String),
    )

def get_consumer():
    """Cria o consumidor Kafka."""
    return KafkaConsumer(
        'iot_sensors',
        bootstrap_servers='kafka:9092',
        auto_offset_reset='earliest',
        group_id='iot-consumer-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

def insert_sensor_data(conn, table, data):
    """Insere dados do sensor na tabela."""
    try:
        with conn.begin():
            conn.execute(table.insert().values(**data))
        logging.info("Inserido com sucesso!")
    except Exception as e:
        logging.error(f"Erro ao inserir: {e}")

def main(): # pragma no cover
    engine = get_engine()
    wait_for_postgres(engine)
    metadata = MetaData()
    sensors_table = create_sensors_table(metadata)
    metadata.create_all(engine)
    wait_for_kafka('kafka', 9092)
    consumer = get_consumer()

    with engine.connect() as conn:
        for message in consumer:
            data = message.value
            logging.info(f"Consumindo: {data}")
            insert_sensor_data(conn, sensors_table, data)

if __name__ == "__main__": # pragma no cover
    main()