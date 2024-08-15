## Log compaction
Log compaction is a mechanism to give finer-grained per-record retention, rather than the coarser-grained time-based retention. The idea is to selectively remove records where we have a more recent update with the same primary key. This way the log is guaranteed to have at least the last state for each key.

Basically what this means is that, for a given message key, Kafka will remove any old messages that have a newer version of it with the same key in the partition log. 

## Setup
Start two consoles and setup them adding the corresponding kafka version tools to the `PATH` and setting the `BROKER` address of the cluster:
```
export PATH="/opt/cesga/kafka/kafka_2.13-3.7.1/bin:$PATH"
export BROKER="10.133.29.20:9092"
```

## Create the topic
Create a topic with appropriate configs
```
kafka-topics.sh --bootstrap-server $BROKER --create --topic lab3.cursoXXX --partitions 1 --replication-factor 1 --config cleanup.policy=compact --config min.cleanable.dirty.ratio=0.001 --config segment.ms=100 --config delete.retention.ms=100
```

`segment.ms`: With this option, when Kafka receives a produce request, it will check that the active segment is older than segment.ms value. If it is older, then it will create a new segment. In our command, we set `segment.ms=100` to make sure that a new segment is created when we produce a new message.

The cleaner thread then chooses the log with the highest dirty ratio. This log is called the filthiest log and if its value is greater than `min.cleanable.dirty.ratio` config, it will be cleaned.

## Describe it
Describe the topic configs
```
kafka-topics.sh --bootstrap-server $BROKER --describe --topic lab3.cursoXXX
```

## Log compaction in action
See it in action:
- Console 1: Start a consumer
    ```
    kafka-console-consumer.sh --bootstrap-server $BROKER --topic lab3.cursoXXX --from-beginning --property print.key=true --property key.separator=:
    ```
- Console 2: start publishing data to the topic
    ```
    kafka-console-producer.sh --bootstrap-server $BROKER --topic lab3.cursoXXX --property parse.key=true --property key.separator=:
    >item0:my item 0 V0
    >item1:my item 1 V0
    >item2:my item 2 V0
    >item0:my item 0 V1
    >item0:my item 0 V2
    >item0:my item 0 V3
    >item0:my item 0 V4
    >item1:my item 1 V1
    >item1:my item 1 V2
    >item1:my item 1 V3
    >item1:my item 1 V4
    >item2:my item 2 V1
    >item3:my item 3 V0
    >item3:my item 3 V1
    ```
- Console 1: Stop the consumer and start it again to see what keys have been already compacted
    ```
    kafka-console-consumer.sh --bootstrap-server $BROKER --topic lab3.cursoXXX --from-beginning --property print.key=true --property key.separator=:
    ```

## References
- [Kafka log compacted topics](https://towardsdatascience.com/log-compacted-topics-in-apache-kafka-b1aa1e4665a7)
