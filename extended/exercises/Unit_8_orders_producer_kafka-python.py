from kafka import KafkaProducer
import json
import random
import time
from datetime import datetime

def products():
    """Generates the list of products in the order"""
    products = []
    for p in range(random.randint(1, 5)):
        products.append({"product_id": random.randint(1, 100), "count": random.randint(1, 4)})
    return products


producer = KafkaProducer(bootstrap_servers='10.38.28.103:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

order_id = 1
while True:
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    order = {"order_id": order_id, "created_at": created_at, "products": products(), "customer_id": random.randint(1, 1000)}
    print(order)
    producer.send('orders', value=order)
    producer.flush()
    order_id += 1
    time.sleep(1)
