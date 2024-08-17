"""Consumer using kafka-python module and value_deserializer

Reads configuration from the following environmental variables:
    - BROKER: Kafka Broker, it can include port eg. "10.38.28.103:9092"
    - TOPIC: Kafka Topic eg. "test.cursoXXX"

You can store the configuration variables in a file and then load them:

    source ~/bash/kafka

You can send messages using:

    kafka-console-producer.sh --bootstrap-server $BROKER --topic $TOPIC --property parse.key=true --property key.separator=:

"""
from kafka import KafkaConsumer
import json
import os


broker = os.environ['BROKER']
topic = os.environ['TOPIC']

consumer = KafkaConsumer(topic, bootstrap_servers=broker,
                         value_deserializer=lambda v: json.loads(v.decode('utf-8')))

for message in consumer:
    print(message)
