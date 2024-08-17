"""Consumer using kafka-python module

Reads configuration from the following environmental variables:
    - BROKER: Kafka Broker, it can include port eg. "10.38.28.103:9092"
    - TOPIC: Kafka Topic eg. "test.cursoXXX"

You can store the configuration variables in a file and then load them:

    source ~/bash/kafka

You can send messages using:

    kafka-console-producer.sh --bootstrap-server $BROKER --topic $TOPIC --property parse.key=true --property key.separator=:

"""
from kafka import KafkaConsumer
import os


broker = os.environ['BROKER']
topic = os.environ['TOPIC']

consumer = KafkaConsumer(topic, bootstrap_servers=broker)

for message in consumer:
    print(message)
