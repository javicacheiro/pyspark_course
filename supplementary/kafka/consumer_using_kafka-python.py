"""Consumer using kafka-python module

Reads configuration from the following environmental variables:
    - KAFKA_BROKER: Kafka Broker, it can include port eg. "10.38.28.103:9092"

You can store the configuration variables in a file and then load them:

    source ~/bash/kafka

"""
from kafka import KafkaConsumer
import os


broker = os.environ['KAFKA_BROKER']

consumer = KafkaConsumer('test.curso800', bootstrap_servers=broker)

for message in consumer:
    print(message)
