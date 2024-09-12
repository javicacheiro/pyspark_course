# Kakfa CLI
Let's review the Kakfa CLI tools provided with Kafka.

## Bootstrap server vs Zookeeper option
Since kafka has been using zookeeper for a long time it was common to indicate the location of the kafka cluster using the `--zookeeper` option and pointing to the zookeeper addresses.

Nowadays the `--zookeeper` option has been deprecated and Zookeeper will be progressively replaced with KRaft.

In the past there was a lot of confussion because some commands did not supported the new `--bootstrap-server` option.

In all our examples we will use the `--bootstrap-server` but keep this in mind if you have to deal with old kafka installations or if you find information about previous versions when searching in the web.

## Setup
Since we are going to use this option a lot we will store the address of our broker (one address is enough) in a variable:
```bash
export BROKER="10.133.29.20:9092"
```

For convenience we will also add the kafka commands to our path:
```bash
# Option 1: load the kafka module
module load kafka/3.7.1
# Option 2: manually add kafka commands to the path
export PATH="/opt/cesga/kafka/kafka_2.13-3.7.1/bin:$PATH"
```

## Kafka-topics
kafka-topics is used to deal with topic tasks: create, delete, describe, etc

- List current topics

```bash
kafka-topics.sh --bootstrap-server $BROKER --list
```

- Create topic:
```bash
# With default options
kafka-topics.sh --bootstrap-server $BROKER --topic test1.cursoXXX --create
# With the given number of partitions
kafka-topics.sh --bootstrap-server $BROKER --topic test2.cursoXXX --create --partitions 2
# With the given number of partitions and replication factor
kafka-topics.sh --bootstrap-server $BROKER --topic test3.cursoXXX --create --partitions 3 --replication-factor 1
# We can not use a higher replication factor than the number of brokers in the cluster
kafka-topics.sh --bootstrap-server $BROKER --topic testFAILS.cursoXXX --create --partitions 3 --replication-factor 2
```

- Describe a topic
```bash
kafka-topics.sh --bootstrap-server $BROKER --topic test1.cursoXXX --describe
kafka-topics.sh --bootstrap-server $BROKER --topic test2.cursoXXX --describe
kafka-topics.sh --bootstrap-server $BROKER --topic test3.cursoXXX --describe
```

- We can also get a description of all topics (like a verbose list)
```bash
kafka-topics.sh --bootstrap-server $BROKER --describe
```

- Delete a topic
```bash
kafka-topics.sh --bootstrap-server $BROKER --topic test3.cursoXXX --delete
```

## kakfa-console-producer
In the tools we have at our disposal a simple console producer
```bash
kafka-console-producer.sh --bootstrap-server $BROKER --topic test1.cursoXXX
```
then we can start sending messages (each line will be a message).

The console producer allows us to set also specific properties:
```bash
# Full acks
kafka-console-producer.sh --bootstrap-server $BROKER --topic test1.cursoXXX --producer-property acks=all
```

We can also send the keys separated by `:` or any character that we choose:
```bash
kafka-console-producer.sh --bootstrap-server $BROKER --topic test1.cursoXXX --property parse.key=true --property key.separator=:
>key0:my message
```

If we point our producer to a non-existing topic then by default the new topic will be created using the default options.
```bash
kafka-console-producer.sh --bootstrap-server $BROKER --topic testNA.cursoXXX
>hello
[2022-09-14 14:16:39,567] WARN [Producer clientId=console-producer] Error while fetching metadata with correlation id 4 : {testNA.cursoXXX=LEADER_NOT_AVAILABLE} (org.apache.kafka.clients.NetworkClient)
>world
```

You can then check that it has been created:
```bash
kafka-topics.sh --bootstrap-server $BROKER --topic testNA.cursoXXX --describe
```

The default topic creation options can be set in the kakfa `server.properties` file.

The best practice is to always create the topic before sending messages to it.

## kafka-console-consumer
As in the case of the producer, in the tools we have at our disposal a simple console consumer

```bash
kafka-console-consumer.sh --bootstrap-server $BROKER --topic test1.cursoXXX
```

By default it consumes just new messages, but we can request also old messages (offset):
```bash
kafka-console-consumer.sh --bootstrap-server $BROKER --topic test1.cursoXXX --from-beginning
```

We can also print the keys of the messages:
```bash
kafka-console-consumer.sh --bootstrap-server $BROKER --topic lab1.cursoXXX --from-beginning --property print.key=true --property key.separator=:
```

It also supports creating consumer groups.

Create a consumer group:
```bash
# consumer-group-1
kafka-console-consumer.sh --bootstrap-server $BROKER --topic test1.cursoXXX --group consumer-group-1
kafka-console-consumer.sh --bootstrap-server $BROKER --topic test1.cursoXXX --group consumer-group-1
```

We can create additional consumer groups:
```bash
# consumer-group-2
kafka-console-consumer.sh --bootstrap-server $BROKER --topic test1.cursoXXX --group consumer-group-2
kafka-console-consumer.sh --bootstrap-server $BROKER --topic test1.cursoXXX --group consumer-group-2
```

And at the same time also consume from an individual consumer
```bash
kafka-console-consumer.sh --bootstrap-server $BROKER --topic test1.cursoXXX
```

## kafka-consumer-groups
In the CLI we have a specific command to manage consumer groups.

- List created consumer groups:
```bash
kafka-consumer-groups.sh --bootstrap-server $BROKER --list
```

- Describe a consumer group
```bash
kafka-consumer-groups.sh --bootstrap-server $BROKER --group consumer-group-2 --describe
```

The command allows also to modify the offsets. We first stop the consumer group and then we can:

- Reset the offsets so they point again to the beginning of each partition of a given topic
```bash
kafka-consumer-groups.sh --bootstrap-server $BROKER --group consumer-group-2 --topic test1.cursoXXX --reset-offsets --to-earliest --execute
```

- Shift the offset forward by 10
```bash
kafka-consumer-groups.sh --bootstrap-server $BROKER --group consumer-group-2 --topic test1.cursoXXX --reset-offsets --shift-by 10 --execute
```

- Shift the offset backward by 10
```bash
kafka-consumer-groups.sh --bootstrap-server $BROKER --group consumer-group-2 --topic test1.cursoXXX --reset-offsets --shift-by -10 --execute
```

These commands modify the `__consumer_offsets` topic.

After that if we start again the consumers in the consumer group we will see the effects.

## kafka-configs
The `kafka-configs` tools allows as to modify topic configurations.

Let's first describe an existing topic:
```bash
kafka-topics.sh --bootstrap-server $BROKER --topic test2.cursoXXX --describe
```

Describe the dynamic configs for the previous topic:
```bash
kafka-configs.sh --bootstrap-server $BROKER --entity-type topics --entity-name test2.cursoXXX --describe
```

Let's set a config so the min ISR of our topic is 2:
```bash
kafka-configs.sh --bootstrap-server $BROKER --entity-type topics --entity-name test2.cursoXXX --add-config min.insync.replicas=3 --alter
```

Let's describe again the dynamic configs of our topic:
```bash
kafka-configs.sh --bootstrap-server $BROKER --entity-type topics --entity-name test2.cursoXXX --describe
```

Delete the config:
```bash
kafka-configs.sh --bootstrap-server $BROKER --entity-type topics --entity-name test2.cursoXXX --delete-config min.insync.replicas --alter
```

Verify that the config has been deleted:
```bash
kafka-configs.sh --bootstrap-server $BROKER --entity-type topics --entity-name test2.cursoXXX --describe
```

## Retention period
By default the retention period is 7 days.

This is a global configuration that is configured in `server.settings`:
```
log.retention.hours=168
```

We can modify it, in a per-topic basis, using the `kakfa-configs` tool.

Change the retention period of our topic to 1 hour:
```bash
kafka-configs.sh --bootstrap-server $BROKER --entity-type topics --add-config retention.ms=3600000 --entity-name test2.cursoXXX --alter
```

Delete the config:
```bash
kafka-configs.sh --bootstrap-server $BROKER --entity-type topics --entity-name test2.cursoXXX --delete-config retention.ms --alter
```

## References
- [Kafka tools](https://docs.confluent.io/kafka/operations-tools/kafka-tools.html)
- [Kafka operations](https://kafka.apache.org/documentation/#operations)

## Exercises
- Lab 1: [Console producer](exercises/1_console_producer.md)
- Lab 2: [Consumer groups](exercises/2_consumer_groups.md)
- Lab 3 (optional): [Log compation](exercises/3_log_compation.md)
