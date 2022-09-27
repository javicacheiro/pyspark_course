"""Producer using confluent-kafka module

Reads configuration from the following environmental variables:
    - KAFKA_BROKER: Kafka Broker, it can include port eg. "10.38.28.103:9092"

You can store the configuration variables in a file and then load them:

    source ~/bash/kafka

Remember to create the Kafka topic first using something similar to:

    kafka-topics.sh --bootstrap-server $BROKER --topic test.curso800 --create --partitions 3 --replication-factor 1

You can consume the messages using:

    kafka-console-consumer.sh --bootstrap-server $BROKER --topic test.curso800 --property print.key=true,key.separator=:

this way you will also see the keys sent.
"""
from confluent_kafka import Producer
import socket
import json
import os


broker = os.environ['KAFKA_BROKER']

conf = {'bootstrap.servers': broker, 'client.id': socket.gethostname()}

producer = Producer(conf)

topic = 'test.curso800'

producer.produce(topic, value='My first message from confluent_kafka!')
producer.produce(topic, key=b'100', value='My second message from confluent_kafka!')
producer.produce(topic, value='{"order_id": 11, "products": [2, 5]}')
order = {"order_id": 12, "products": [2, 5]}
producer.produce(topic, value=json.dumps(order))
producer.flush()
