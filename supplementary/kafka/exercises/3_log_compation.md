## Log compation
Log compaction is a mechanism to give finer-grained per-record retention, rather than the coarser-grained time-based retention. The idea is to selectively remove records where we have a more recent update with the same primary key. This way the log is guaranteed to have at least the last state for each key.

Basically what this means is that for a given message key, Kafka will remove any old messages that have a newer version of it with the same key in the partition log. 

Create a topic with appropriate configs
```
kafka-topics.sh --bootstrap-server $BROKER --create --topic items.curso800 --partitions 1 --replication-factor 1 --config cleanup.policy=compact --config min.cleanable.dirty.ratio=0.001 --config segment.ms=5000 --config delete.retention.ms=100
```

Describe the topic configs
```
kafka-topics.sh --bootstrap-server $BROKER --describe --topic items.curso800
```

See it in action:
- Console 1: Start a consumer
    ```
    kafka-console-consumer.sh --bootstrap-server $BROKER --topic items.curso800 --from-beginning --property print.key=true --property key.separator=:
    ```
- Console 2: start publishing data to the topic
    ```
    kafka-console-producer.sh --bootstrap-server $BROKER --topic items.curso800 --property parse.key=true --property key.separator=:
    >item0:my item 0
    >item1:my item 1
    >item2:my item 2
    >item0:my renamed item 0
    ```

segment.ms: With this option, when Kafka receives a produce request, it will check that the active segment is older than segment.ms value. If it is older, then it will create a new segment. In our command, we set segment.ms=100 to make sure that every 100 milliseconds a new segment is created.

The cleaner thread then chooses the log with the highest dirty ratio. This log is called the filthiest log and if its value is greater than min.cleanable.dirty.ratio config, it will be cleaned.

For more details:
- https://towardsdatascience.com/log-compacted-topics-in-apache-kafka-b1aa1e4665a7
