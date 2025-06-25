import pytest
from unittest.mock import patch, MagicMock
from faker import Faker
from producer.producer import (
    generate_sensor_data,
    create_kafka_producer,
    wait_for_kafka
)

def test_generate_sensor_data():
    fake = Faker()
    data = generate_sensor_data(fake)
    assert "sensor_id" in data
    assert "location" in data
    assert 20.0 <= data["temperature"] <= 40.0
    assert 30.0 <= data["humidity"] <= 90.0
    assert "timestamp" in data

@patch('producer.producer.KafkaProducer')
def test_create_kafka_producer(mock_kafka_producer):
    mock_instance = MagicMock()
    mock_kafka_producer.return_value = mock_instance
    producer_instance = create_kafka_producer()
    assert producer_instance == mock_instance
    mock_kafka_producer.assert_called_once()

@patch('socket.create_connection')
def test_wait_for_kafka(mock_create_connection):
    mock_create_connection.return_value = MagicMock()
    # Não deve lançar exceção
    wait_for_kafka('localhost', 9092, retry_interval=0)
    mock_create_connection.assert_called()