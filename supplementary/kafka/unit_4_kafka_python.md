# Using Kafka from Python

# Kakfa Producer
## Module installation
The official module is provided by Confluent, you can install it with conda or with pip, but it requires compilation:
```
# Using conda
conda install -c conda-forge python-confluent-kafka
# Using pip (requires compilation)
pip install confluent-kafka
```

Another alternative, simpler to use, is the [kafka-python](https://github.com/dpkp/kafka-python) module:
```
# Using pip
pip install kafka-python
# Using conda
conda install -c conda-forge -y kafka-python
```

In our case both modules are available loading:
```
module load anaconda3/2022.05
```


## Initialization
```
from confluent_kafka import Producer
import socket

conf = {'bootstrap.servers': "host1:9092,host2:9092",
        'client.id': socket.gethostname()}

producer = Producer(conf)
```

## Asynchronous writes
```
producer.produce(topic, key="key", value="value")
```
NOTE: The `key` is optional, and the `value` can be `None`.

To receive acknowledgements:
```
def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced: %s" % (str(msg)))

producer.produce(topic, key="key", value="value", callback=acked)

# Wait up to 1 second for events. Callbacks will be invoked during
# this method call if the message is acknowledged.
producer.poll(1)
```

## Synchronous writes
Just call the `flush` method to make writes synchronous:
```
producer.produce(topic, key="key", value="value")
producer.flush()
```

# Kafka Consumer
## Initialization
```
from confluent_kafka import Producer
import socket

conf = {'bootstrap.servers': "host1:9092,host2:9092",
        'client.id': socket.gethostname()}

producer = Producer(conf)
```
## Basic poll loop
```
running = True

def basic_consume_loop(consumer, topics):
    try:
        consumer.subscribe(topics)

        while running:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                msg_process(msg)
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

def shutdown():
    running = False
```

## Synchronous commits
The simplest and most reliable way to manually commit offsets is by setting the asynchronous parameter to the Consumer.commit() method call.
```
def consume_loop(consumer, topics):
    try:
        consumer.subscribe(topics)

        msg_count = 0
        while running:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                msg_process(msg)
                msg_count += 1
                if msg_count % MIN_COMMIT_COUNT == 0:
                    consumer.commit(asynchronous=False)
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()
```
A synchronous commit is triggered every MIN_COMMIT_COUNT messages. The asynchronous flag controls whether this call is asynchronous. You could also trigger the commit on expiration of a timeout to ensure there the committed position is updated regularly.

## Delivery guarantees
In the previous example, you get “at least once” delivery since the commit follows the message processing. By changing the order, however, you can get “at most once” delivery, but you must be a little careful with the commit failure.
```
def consume_loop(consumer, topics):
    try:
        consumer.subscribe(topics)

        while running:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                consumer.commit(asynchronous=False)
                msg_process(msg)

    finally:
        # Close down consumer to commit final offsets.
        consumer.close()
```

For simplicity in this example, Consumer.commit() is used prior to processing the message. Committing on every message would produce a lot of overhead in practice. A better approach would be to collect a batch of messages, execute the synchronous commit, and then process the messages only if the commit succeeded.

## Asynchronous Commits
In this example, the consumer sends the request and returns immediately by using asynchronous commits.
```
def consume_loop(consumer, topics):
    try:
        consumer.subscribe(topics)

        msg_count = 0
        while running:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                msg_process(msg)
                msg_count += 1
                if msg_count % MIN_COMMIT_COUNT == 0:
                    consumer.commit(asynchronous=True)
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()
```


# Reference
- [Confluent Kafka Python Client](https://docs.confluent.io/kafka-clients/python/current/overview.html)
