"""Order Producer

Streaming app that uses the kafka-python module to produce orders and
publish them to Kafka in the "orders.curso800" topic.

Reads configuration from the following environmental variables:
    - BROKER: Kafka Broker, it can include port eg. "10.38.28.103:9092"

Requires kafka-python module.
"""
from kafka import KafkaProducer
import json
import random
import time
from datetime import datetime
import os

broker = os.environ['BROKER']


def products():
    """Generates the list of products in the order"""
    products = []
    for p in range(random.randint(1, 5)):
        products.append({"product_id": random.randint(1, 100), "count": random.randint(1, 4)})
    return products


producer = KafkaProducer(bootstrap_servers=broker,
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

order_id = 1
while True:
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    order = {"order_id": order_id, "created_at": created_at, "products": products(), "customer_id": random.randint(1, 1000)}
    print(order)
    producer.send('orders.curso800', value=order)
    producer.flush()
    order_id += 1
    time.sleep(1)
