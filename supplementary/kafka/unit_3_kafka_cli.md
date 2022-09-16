# Kakfa CLI
Let's review the Kakfa CLI tools provided with Kafka.

## Bootstrap server vs Zookeeper option
Since kafka has been using zookeeper for a long time it was common to indicate the location of the kafka cluster using the `--zookeeper` option and pointing to the zookeeper addresses.

Nowadays the `--zookeeper` option has been deprecated (as you know in the future the plan is to move from Zookeeper to Kafka Raft).

Before there was a lot of confussion because some commands did not supported the new `--bootstrap-server` option.

In all our examples we will use the `--bootstrap-server` but keep this in mind if you have to deal with old kafka installations or if you find information about previous versions when searching in the web.

## Setup
Since we are going to use this option a lot we will store the address of our broker (one address is enough) in a variable:
```
export BROKER="10.38.28.103:9092"
```

For convenience we will also add the kafka commands to our path:
```
export PATH="/opt/cesga/kafka/kafka_2.12-3.2.1/bin:$PATH"
```

## Kafka-topics
kafka-topics is used to deal with topic tasks: create, delete, describe, etc

- List current topics

```
kafka-topics.sh --bootstrap-server $BROKER --list
```

- Create topic:
```
# With default options
kafka-topics.sh --bootstrap-server $BROKER --topic test1.curso800 --create
# With the given number of partitions
kafka-topics.sh --bootstrap-server $BROKER --topic test2.curso800 --create --partitions 2
# With the given number of partitions and replication factor
kafka-topics.sh --bootstrap-server $BROKER --topic test3.curso800 --create --partitions 3 --replication-factor 1
# We can not use a higher replication factor than the number of brokers in the cluster
kafka-topics.sh --bootstrap-server $BROKER --topic testFAILS.curso800 --create --partitions 3 --replication-factor 2
```

- Describe a topic
```
kafka-topics.sh --bootstrap-server $BROKER --topic test1.curso800 --describe
kafka-topics.sh --bootstrap-server $BROKER --topic test2.curso800 --describe
kafka-topics.sh --bootstrap-server $BROKER --topic test3.curso800 --describe
```

- We can also get a description of all topics (like a verbose list)
```
kafka-topics.sh --bootstrap-server $BROKER --describe
```

- Delete a topic
```
kafka-topics.sh --bootstrap-server $BROKER --topic test3.curso800 --delete
```

## Kakfa Console Producer
In the tools we have at our disposal a simple console producer
```
kafka-console-producer.sh --bootstrap-server $BROKER --topic test1.curso800
```
then we can start sending messages (each line will be a message).

The console producer allows us to set also specific properties:
```
# Full acks
kafka-console-producer.sh --bootstrap-server $BROKER --topic test1.curso800 --producer-property acks=all
```

If we point our producer to a non-existing topic then by default the new topic will be created using the default options.
```
kafka-console-producer.sh --bootstrap-server $BROKER --topic testNA.curso800
>hello
[2022-09-14 14:16:39,567] WARN [Producer clientId=console-producer] Error while fetching metadata with correlation id 4 : {testNA.curso800=LEADER_NOT_AVAILABLE} (org.apache.kafka.clients.NetworkClient)
>world
```

You can then check that it has been created:
```
kafka-topics.sh --bootstrap-server $BROKER --topic testNA.curso800 --describe
```

The default topic creation options can be set in the kakfa `server.properties` file.

The best practice is to always create the topic before sending messages to it.

## kafka-console-consumer
As in the case of the producer, in the tools we have at our disposal a simple console consumer

```
kafka-console-consumer.sh --bootstrap-server $BROKER --topic test1.curso800
```

By default it consumes just new messages, but we can request also old messages (offset):
```
kafka-console-consumer.sh --bootstrap-server $BROKER --topic test1.curso800 --from-beginning
```

It also supports creating consumer groups.

Create a consumer group:
```
# consumer-group-1
kafka-console-consumer.sh --bootstrap-server $BROKER --topic test1.curso800 --group consumer-group-1
kafka-console-consumer.sh --bootstrap-server $BROKER --topic test1.curso800 --group consumer-group-1
```

We can create additional consumer groups:
```
# consumer-group-2
kafka-console-consumer.sh --bootstrap-server $BROKER --topic test1.curso800 --group consumer-group-2
kafka-console-consumer.sh --bootstrap-server $BROKER --topic test1.curso800 --group consumer-group-2
```

And at the same time also consumer from an individual consumer
```
kafka-console-consumer.sh --bootstrap-server $BROKER --topic test1.curso800
```

## kafka-consumer-groups
In the CLI we have a specific command to manage consumer groups.

- List created consumer groups:
```
kafka-consumer-groups.sh --bootstrap-server $BROKER --list
```

- Describe a consumer group
```
kafka-consumer-groups.sh --bootstrap-server $BROKER --group consumer-group-2 --describe
```

The command allows also to modify the offsets. We first stop the consumer group and then we can:

- Reset the offsets so they point again to the beginning of each partition of a given topic
```
kafka-consumer-groups.sh --bootstrap-server $BROKER --group consumer-group-2 --topic test1.curso800 --reset-offsets --to-earliest --execute
```

- Shift the offset forward by 10
```
kafka-consumer-groups.sh --bootstrap-server $BROKER --group consumer-group-2 --topic test1.curso800 --reset-offsets --shift-by 10 --execute
```

- Shift the offset backward by 10
```
kafka-consumer-groups.sh --bootstrap-server $BROKER --group consumer-group-2 --topic test1.curso800 --reset-offsets --shift-by -10 --execute
```

These commands modify the `__consumer_offsets` topic.

After that if we start again the consumers in the consumer group we will see the effects.

## kafka-configs
The `kafka-configs` tools allows as to modify topic configurations.

Let's first descrite an existing topic:
```
kafka-topics.sh --bootstrap-server $BROKER --topic test2.curso800 --describe
```

Describe the dynamic configs for the previous topic:
```
kafka-configs.sh --bootstrap-server $BROKER --entity-type topics --entity-name test2.curso800 --describe
```

Let's set a config so the min ISR of our topic is 2:
```
kafka-configs.sh --bootstrap-server $BROKER --entity-type topics --entity-name test2.curso800 --add-config min.insync.replicas=3 --alter
```

Let's describe again the dynamic configs of our topic:
```
kafka-configs.sh --bootstrap-server $BROKER --entity-type topics --entity-name test2.curso800 --describe
```

Delete the config:
```
kafka-configs.sh --bootstrap-server $BROKER --entity-type topics --entity-name test2.curso800 --delete-config min.insync.replicas --alter
```

Verify that the config has been deleted:
```
kafka-configs.sh --bootstrap-server $BROKER --entity-type topics --entity-name test2.curso800 --describe
```

## Retention period
By default the retention period is 7 days.

This is a global configuration that is configured in `server.settings`:
```
log.retention.hours=168
```

We can modify it, in a per-topic basis, using the `kakfa-configs` tool.

Change the retention period of our topic to 1 hour:
```
kafka-configs.sh --bootstrap-server $BROKER --entity-type topics --add-config retention.ms=3600000 --entity-name test2.curso800 --alter
```

Delete the config:
```
kafka-configs.sh --bootstrap-server $BROKER --entity-type topics --entity-name test2.curso800 --delete-config retention.ms --alter
```

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
    kafka-console-consumer.sh --bootstrap-server $BROKER --topic items.curso800 --from-beginning --property print.key=true --property key.separator=,
    ```
- Console 2: start publishing data to the topic
    ```
    kafka-console-producer.sh --bootstrap-server $BROKER --topic items.curso800 --property parse.key=true --property key.separator=,
    >item0,my item 0
    >item1,my item 1
    >item2,my item 2
    >item0,my renamed item 0
    ```

segment.ms: With this option, when Kafka receives a produce request, it will check that the active segment is older than segment.ms value. If it is older, then it will create a new segment. In our command, we set segment.ms=100 to make sure that every 100 milliseconds a new segment is created.

The cleaner thread then chooses the log with the highest dirty ratio. This log is called the filthiest log and if its value is greater than min.cleanable.dirty.ratio config, it will be cleaned.

For more details:
- https://towardsdatascience.com/log-compacted-topics-in-apache-kafka-b1aa1e4665a7
