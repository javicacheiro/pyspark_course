# Consumer Groups Lab
## Setup
Start four consoles and setup them adding the corresponding kafka version tools to the `PATH` and setting the `BROKER` address of the cluster:
```
export PATH="/opt/cesga/kafka/kafka_2.13-3.7.1/bin:$PATH"
export BROKER="10.133.29.20:9092"
```

## Create the topic
Create a topic with 3 partitions
```
kafka-topics.sh --bootstrap-server $BROKER --topic lab2.cursoXXX --create --partitions 3 --replication-factor 1
```

## Start the consumers
Start 3 consumers each in one console:
- Console 1:
```
kafka-console-consumer.sh --bootstrap-server $BROKER --topic lab2.cursoXXX --group consumer-group-1-cursoXXX --property print.key=true --property key.separator=:
```
- Console 2:
```
kafka-console-consumer.sh --bootstrap-server $BROKER --topic lab2.cursoXXX --group consumer-group-1-cursoXXX --property print.key=true --property key.separator=:
```
- Console 3:
```
kafka-console-consumer.sh --bootstrap-server $BROKER --topic lab2.cursoXXX --group consumer-group-1-cursoXXX --property print.key=true --property key.separator=:
```

## Start the producer
In a new console start sending messages:
- Console 4:
```
kafka-console-producer.sh --bootstrap-server $BROKER --topic lab2.cursoXXX --property parse.key=true --property key.separator=:
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

Keep sending messages.

## Stop one consumer
Kill one member of the consumer group and see how the others consume its messages.

## Start again the stopped consumer
Start it again and see how it starts consuming again.
