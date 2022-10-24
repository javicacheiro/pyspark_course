"""Consumer using kafka-python module

Reads configuration from the following environmental variables:
    - KAFKA_BROKER: Kafka Broker, it can include port eg. "10.38.28.103:9092"

You can store the configuration variables in a file and then load them:

    source ~/bash/kafka

"""
from kafka import KafkaConsumer
import json
import os


broker = os.environ['KAFKA_BROKER']

consumer = KafkaConsumer('test.curso800', bootstrap_servers=broker,
                         value_deserializer=lambda v: json.loads(v.decode('utf-8')))

for message in consumer:
    print(message)
