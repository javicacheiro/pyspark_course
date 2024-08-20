# Using Kafka from Python

# Kakfa Producer
## Module installation
The official module is provided by Confluent, you can install it with conda or with pip, but it requires compilation:
```bash
# Using conda
conda install -c conda-forge python-confluent-kafka
# Using pip (requires compilation)
pip install confluent-kafka
```

Another alternative, simpler to use, is the [kafka-python](https://github.com/dpkp/kafka-python) module:
```bash
# Using pip
pip install kafka-python
# Using conda
conda install -c conda-forge -y kafka-python
```

In our case both modules are available loading:
```bash
module load anaconda3/2024.02-1
```

## Initialization
```python
from confluent_kafka import Producer
import socket

conf = {'bootstrap.servers': "host1:9092,host2:9092",
        'client.id': socket.gethostname()}

producer = Producer(conf)
```

## Asynchronous writes
```python
producer.produce(topic, key="key", value="value")
```
NOTE: The `key` is optional, and the `value` can be `None`.

To receive acknowledgements:
```python
def acked(err, msg):
    if err is not None:
        print(f"Failed to deliver message: {msg}: {err}")
    else:
        print(f"Message produced: {msg}")

producer.produce(topic, key="key", value="value", callback=acked)

# Wait up to 1 second for events. Callbacks will be invoked during
# this method call if the message is acknowledged.
producer.poll(1)
```

## Synchronous writes
Just call the `flush` method to make writes synchronous:
```python
producer.produce(topic, key="key", value="value")
producer.flush()
```

# Kafka Consumer
## Initialization
```python
from confluent_kafka import Consumer

conf = {'bootstrap.servers': "host1:9092,host2:9092",
        'group.id': "consumer_group_name"}

consumer = Consumer(conf)
```
## Basic poll loop
```python
try:
    consumer.subscribe(['topic1', 'topic2'])
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None: continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                print(f'%% {msg.topic} [{msg.partition}] reached end at offset {msg.offset}\n')
            else:
                raise KafkaException(msg.error())
        else:
            print(msg.key(), msg.value())
finally:
    # Close down consumer to commit final offsets.
    consumer.close()
```

## Synchronous commits
The simplest and most reliable way to manually commit offsets is by setting the asynchronous parameter to the Consumer.commit() method call.
```python
# Commit at least every 10 messages
MIN_COMMIT_COUNT = 10
try:
    consumer.subscribe(['topic1', 'topic2'])
    count = 0
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None: continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                print(f'%% {msg.topic} [{msg.partition}] reached end at offset {msg.offset}\n')
            else:
                raise KafkaException(msg.error())
        else:
            process_message(msg)
            count += 1
            if count % MIN_COMMIT_COUNT == 0:
                consumer.commit(asynchronous=False)
finally:
    consumer.close()
```
A synchronous commit is triggered every MIN_COMMIT_COUNT messages. The asynchronous flag controls whether this call is asynchronous. You could also trigger the commit on expiration of a timeout to ensure the committed position is updated regularly.

## Delivery guarantees
In the previous example, you get **at least once** delivery since the commit follows the message processing. By changing the order, however, you can get **at most once** delivery, but you must be a little careful if there is a commit failure.
```python
try:
    consumer.subscribe(['topic1', 'topic2'])
    count = 0
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None: continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                print(f'%% {msg.topic} [{msg.partition}] reached end at offset {msg.offset}\n')
            else:
                raise KafkaException(msg.error())
        else:
            consumer.commit(asynchronous=False)
            process_message(msg)
finally:
    consumer.close()
```

Committing on every message would produce a lot of overhead in practice. A better approach would be to collect a batch of messages, execute the synchronous commit, and then process the messages only if the commit succeeded.

## Asynchronous Commits
In this example, the consumer sends the request and returns immediately by using asynchronous commits. In this case we also batch the messages.
```python
# Commit at least every 10 messages
MIN_COMMIT_COUNT = 10
try:
    consumer.subscribe(['topic1', 'topic2'])
    count = 0
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None: continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                print(f'%% {msg.topic} [{msg.partition}] reached end at offset {msg.offset}\n')
            else:
                raise KafkaException(msg.error())
        else:
            process_message(msg)
            count += 1
            if count % MIN_COMMIT_COUNT == 0:
                consumer.commit(asynchronous=True)
finally:
    consumer.close()
```

## Exercises
Review the code and each of the following examples:
- [Producer using Confluent Kafka](exercises/producer_using_confluent_kafka.py)
- [Producer using kafka-python](exercises/producer_using_kafka-python.py)
- [Producer using kafka-python: sending JSON using value_serializer](exercises/producer_using_kafka-python_json.py)
- [Consumer using Confluent Kafka](exercises/consumer_using_confluent_kafka.py)
- [Consumer using kafka-python](exercises/consumer_using_kafka-python.py)
- [Consumer using kafka-python: consuming JSON using value_deserializer](exercises/consumer_using_kafka-python_json.py)

Remember to load the anaconda3 module that provides access to both kafka-python and confluent kafka:
```
module load anaconda3/2024.02-1
```
The examples read the `BROKER` and `TOPIC` information from the environment, so remember to set them accordingly to your setup:
```
export BROKER="10.133.29.20:9092"
export TOPIC="test.cursoXXX"
```
You can use kafka tools to see the messages that are being published or to produce new messages.
```
module load kafka/3.7.1
```

## References
- [Confluent Kafka Python Client](https://docs.confluent.io/kafka-clients/python/current/overview.html)
- [Kafka-python Client](https://kafka-python.readthedocs.io/en/master/)
