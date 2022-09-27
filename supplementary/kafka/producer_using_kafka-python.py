"""Producer using kafka-python

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
from kafka import KafkaProducer
import json
import os


broker = os.environ['KAFKA_BROKER']

producer = KafkaProducer(bootstrap_servers=broker)

producer.send('test.curso800', b'My first message!')
producer.send('test.curso800', key=b'123', value=b'My second message!')
producer.send('test.curso800', value=b'{"order_id": 1, "products": [1, 5, 4]}')
order = {"order_id": 2, "products": [2, 5]}
producer.send('test.curso800', value=json.dumps(order).encode('utf8'))
producer.flush()
