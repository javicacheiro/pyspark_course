# Consumer Groups Lab
Create a topic with 3 partitions
```
kafka-topics.sh --bootstrap-server $BROKER --topic lab2.curso800 --create --partitions 3 --replication-factor 1
```

Start 3 consumers:
```
kafka-console-consumer.sh --bootstrap-server $BROKER --topic lab2.curso800 --group consumer-group-1
kafka-console-consumer.sh --bootstrap-server $BROKER --topic lab2.curso800 --group consumer-group-1
kafka-console-consumer.sh --bootstrap-server $BROKER --topic lab2.curso800 --group consumer-group-1
```

Start sending messages:
```
kafka-console-consumer.sh --bootstrap-server $BROKER --topic lab2.curso800 --group consumer-group-1
>key0:message 0
>key1:message 1
>key2:message 2
>key3:message 3
>key4:message 4
>key5:message 5
>key6:message 6
>key0:message 00
>key1:message 10
>key2:message 20
>key3:message 30
>key4:message 40
>key5:message 50
>key6:message 60
```

See how the messages are spread between the consumers in the consumer group depending on the value of the key (same key goes to the same consumer).

Kill one member of the consumer group and see how the others consume its messages.

Start it again and see how it starts consuming again.
