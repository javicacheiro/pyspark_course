"""Producer using kafka-python

Reads configuration from the following environmental variables:
    - BROKER: Kafka Broker, it can include port eg. "10.38.28.103:9092"

You can store the configuration variables in a file and then load them:

    source ~/bash/kafka

Remember to create the Kafka topic first using something similar to:

    kafka-topics.sh --bootstrap-server $BROKER --topic test.cursoXXX --create --partitions 3 --replication-factor 1

You can consume the messages using:

    kafka-console-consumer.sh --bootstrap-server $BROKER --topic test.cursoXXX --property print.key=true,key.separator=:

this way you will also see the keys sent.
"""
from kafka import KafkaProducer
import json
import os


broker = os.environ['BROKER']

producer = KafkaProducer(bootstrap_servers=broker)

producer.send('test.cursoXXX', b'My first message!')
producer.send('test.cursoXXX', key=b'123', value=b'My second message!')
producer.send('test.cursoXXX', value=b'{"order_id": 1, "products": [1, 5, 4]}')
order = {"order_id": 2, "products": [2, 5]}
producer.send('test.cursoXXX', value=json.dumps(order).encode('utf8'))
producer.flush()
