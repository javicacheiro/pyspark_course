from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='10.38.28.103:9092')

#producer.send('orders2', value=b'{"order_id": 0, "school_book_pack": 100}')
producer.send('orders', b'Hello, World!')
producer.flush()
#producer.send('orders2', key=b'0', value=b'Hello, World!')
