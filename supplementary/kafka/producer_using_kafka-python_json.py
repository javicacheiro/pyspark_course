from kafka import KafkaProducer
import json

producer = KafkaProducer(bootstrap_servers='10.38.28.103:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

order = {"order_id": 0, "school_book_pack": 100}
producer.send('orders', value=order)
producer.flush()
