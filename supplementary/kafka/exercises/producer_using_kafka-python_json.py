"""Producer using kafka-python module and value_serializer

Reads configuration from the following environmental variables:
    - BROKER: Kafka Broker, it can include port eg. "10.38.28.103:9092"
    - TOPIC: Kafka Topic eg. "test.cursoXXX"

You can store the configuration variables in a file and then load them:

    source ~/bash/kafka

Remember to create the Kafka topic first using something similar to:

    kafka-topics.sh --bootstrap-server $BROKER --topic $TOPIC --create --partitions 3 --replication-factor 1

You can consume the messages using:

    kafka-console-consumer.sh --bootstrap-server $BROKER --topic $TOPIC --property print.key=true --property key.separator=:

this way you will also see the keys sent.
"""
from kafka import KafkaProducer
import json
import os


broker = os.environ['BROKER']
topic = os.environ['TOPIC']

producer = KafkaProducer(bootstrap_servers=broker,
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

order = {"order_id": 2, "products": [2, 5]}
producer.send(topic, value=order)
producer.flush()
