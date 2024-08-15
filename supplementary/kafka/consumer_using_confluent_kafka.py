"""Consumer using confluent-kafka module

Reads configuration from the following environmental variables:
    - BROKER: Kafka Broker, it can include port eg. "10.38.28.103:9092"

You can store the configuration variables in a file and then load them:

    source ~/bash/kafka

"""
from __future__ import print_function
from confluent_kafka import Consumer, KafkaError, KafkaException
import os


broker = os.environ['BROKER']

conf = {'bootstrap.servers': broker,
        'group.id': 'curso800.group',
        'enable.auto.commit': False,
        'auto.offset.reset': 'earliest'}

consumer = Consumer(conf)

topics = ['test.curso800', 'test.curso801']
consumer.subscribe(topics)

try:
    while True:
        message = consumer.poll(timeout=1.0)
        if message is not None:
            if message.error():
                if message.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    print('%% {} [{}] reached end at offset {}\n'.format(
                        message.topic(), message.partition(), message.offset()))
                elif message.error():
                    raise KafkaException(message.error())
            else:
                consumer.commit(asynchronous=False)
                print(message.key(), message.value())
finally:
    consumer.close()
