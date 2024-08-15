# Console producer
In this lab we are going to create a topic and then publish some messages to it that we will consume using a console consumer.

## Setup
Add the corresponding kafka version tools to the `PATH` and set the `BROKER` address of the cluster:
```
export PATH="/opt/cesga/kafka/kafka_2.13-3.7.1/bin:$PATH"
export BROKER="10.133.29.20:9092"
```

## Create the topic
First we will list current topics
```
kafka-topics.sh --bootstrap-server $BROKER --list
```

The we will create a topic named `lab1.cursoXXX` with the number corresponding to our account and with 3 partitions and 1 replica
```
kafka-topics.sh --bootstrap-server $BROKER --topic lab1.cursoXXX --create --partitions 3 --replication-factor 1
```

Let's verify that our topic has been created
```
kafka-topics.sh --bootstrap-server $BROKER --list
```

And we can also verify that it has the right options:
```
kafka-topics.sh --bootstrap-server $BROKER --topic lab1.cursoXXX --describe
```

## Send some messages
We will start a console producer and from here we will send some messages with key and value separated by `:`
```
kafka-console-producer.sh --bootstrap-server $BROKER --topic lab1.cursoXXX --property parse.key=true --property key.separator=:
>key1:my first message
>key2:my second message
```
To exit the console producer type: `Ctrl+d`

## Start the console consumer
We will start a console consumer and we will configure it to show the messages from the beginning and to display also the keys:
```
kafka-console-consumer.sh --bootstrap-server $BROKER --topic lab1.cursoXXX --from-beginning --property print.key=true --property key.separator=:
```
