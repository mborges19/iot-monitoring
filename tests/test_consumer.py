import pytest
from unittest.mock import patch, MagicMock
from consumer.consumer import (
    create_sensors_table,
    get_consumer,
    wait_for_kafka,
    get_engine,
    insert_sensor_data
)

def test_create_sensors_table():
    metadata = MagicMock()
    table = create_sensors_table(metadata)
    assert table.name == 'sensors'
    columns = [col.name for col in table.columns]
    assert set(columns) == {'sensor_id', 'location', 'temperature', 'humidity', 'timestamp'}

@patch('consumer.consumer.KafkaConsumer')
def test_get_consumer(mock_kafka_consumer):
    mock_instance = MagicMock()
    mock_kafka_consumer.return_value = mock_instance
    consumer_instance = get_consumer()
    assert consumer_instance == mock_instance
    mock_kafka_consumer.assert_called_once()

@patch('socket.create_connection')
def test_wait_for_kafka(mock_create_connection):
    mock_create_connection.return_value = MagicMock()
    wait_for_kafka('localhost', 9092, retry_interval=0)
    mock_create_connection.assert_called()

@patch('consumer.consumer.create_engine')
def test_get_engine(mock_create_engine):
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    engine = get_engine()
    assert engine == mock_engine
    mock_create_engine.assert_called_once()

def test_insert_sensor_data_success():
    conn = MagicMock()
    table = MagicMock()
    data = {"sensor_id": "1", "location": "A", "temperature": 25.0, "humidity": 50.0, "timestamp": "2024-01-01T00:00:00"}
    insert_sensor_data(conn, table, data)
    conn.begin.assert_called_once()
    conn.execute.assert_called_once()

def test_insert_sensor_data_exception(caplog):
    conn = MagicMock()
    table = MagicMock()
    conn.execute.side_effect = Exception("erro")
    data = {"sensor_id": "1", "location": "A", "temperature": 25.0, "humidity": 50.0, "timestamp": "2024-01-01T00:00:00"}
    with caplog.at_level("ERROR"):
        insert_sensor_data(conn, table, data)
        assert "Erro ao inserir" in caplog.text