from confluent_kafka import Producer
import socket
import json

conf = {'bootstrap.servers': '10.38.28.103:9092', 'client.id': socket.gethostname()}

producer = Producer(conf)

# We create the "orders" topic:
# >> kafka-topics.sh --bootstrap-server $BROKER --topic orders --create --partitions 3 --replication-factor 1
topic = 'orders'

order = {"order_id": 0, "school_book_pack": 100}
#producer.produce(topic, value=json.dumps(order))
producer.produce(topic, value='{"order_id": 0, "school_book_pack": 100}')
producer.flush()
