from kafka import KafkaConsumer

consumer = KafkaConsumer('orders', bootstrap_servers='10.38.28.103:9092')

for message in consumer:
    print (message)
