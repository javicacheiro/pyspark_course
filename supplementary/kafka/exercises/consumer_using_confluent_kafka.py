"""Consumer using confluent-kafka module

Reads configuration from the following environmental variables:
    - BROKER: Kafka Broker, it can include port eg. "10.38.28.103:9092"
    - TOPIC: Kafka Topic eg. "test.cursoXXX"

You can store the configuration variables in a file and then load them:

    source ~/bash/kafka

You can send messages using:

    kafka-console-producer.sh --bootstrap-server $BROKER --topic $TOPIC --property parse.key=true --property key.separator=:

"""
from __future__ import print_function
from confluent_kafka import Consumer, KafkaError, KafkaException
import os


broker = os.environ['BROKER']
topic = os.environ['TOPIC']

conf = {'bootstrap.servers': broker,
        'group.id': os.environ['USER']+'.group',
        'enable.auto.commit': False,
        'auto.offset.reset': 'earliest',
        # Emit event when the consumer reaches the end of a partition.
        'enable.partition.eof': True}

consumer = Consumer(conf)

topics = [topic]

try:
    consumer.subscribe(topics)
    while True:
        message = consumer.poll(timeout=1.0)
        if message is None: continue
        if message.error():
            if message.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                print('%% {} [{}] reached end at offset {}\n'.format(
                    message.topic(), message.partition(), message.offset()))
            else:
                raise KafkaException(message.error())
        else:
            consumer.commit(asynchronous=False)
            print(message.key(), message.value())
finally:
    consumer.close()
