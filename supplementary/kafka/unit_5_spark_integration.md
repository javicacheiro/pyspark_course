# Spark Integration
## Using Kafka from Spark (default version)
### Verify Spark and Scala versions
Verify the scala version of our Spark installation running `spark-shell`:
```
[jlopez@cdh61-login3 ~]$ spark-shell
Spark context Web UI available at http://cdh61-login3.bd.cluster.cesga.es:4040
Spark context available as 'sc' (master = yarn, app id = application_1650627462529_4948).
Spark session available as 'spark'.
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /___/ .__/\_,_/_/ /_/\_\   version 2.4.0-cdh6.1.1
      /_/

Using Scala version 2.11.12 (Java HotSpot(TM) 64-Bit Server VM, Java 1.8.0_191)
Type in expressions to have them evaluated.
Type :help for more information.

scala>
```
As we can see in our case with have spark 2.4.0-cdh6.1.1 compiled with scala 2.11.12.

### Look for the apropriate connector
We go to the maven repository and we have to locate the required connector to use kafka with spark:
- For structured streaming we have to look in:
   - [spark-sql-kafka-0-10: Kafka 0.10+ Source For Structured Streaming](https://mvnrepository.com/artifact/org.apache.spark/spark-sql-kafka-0-10)
- For the legacy DStream API we would look for:
   - [spark-streaming-kafka-0-10: Spark Integration For Kafka 0.10](https://mvnrepository.com/artifact/org.apache.spark/spark-streaming-kafka-0-10)

In the most common case that we want to use structured streaming, we locate the connector corresponding to our spark and scala version, in our case spark 2.4.0 and scala 2.11.
- https://mvnrepository.com/artifact/org.apache.spark/spark-sql-kafka-0-10_2.11/2.4.0

In this page we look for the groupId, artifactId and version:
```
<dependency>
    <groupId>org.apache.spark</groupId>
    <artifactId>spark-sql-kafka-0-10_2.11</artifactId>
    <version>2.4.0</version>
    <scope>test</scope>
</dependency>
```

### Run spark with this connector
Then to use it we just have to pass the groupId, artifactId and version to the `--packages` option of `spark-submit` as `--packages groupId:artifactId:version` and it will download automatically the jar file:
```
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.0 your_app.py
```

For example you can use the provided example spark streaming consumer job that consumes data from a given topic (it expects the BROKER and TOPIC env variables):
```
export BROKER="10.133.29.20:9092"
export TOPIC="lab2.cursoXXX"
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.0 exercises/spark_kafka_example.py
```

## Using Kafka from Spark 3.4.3
### Verify Spark and Scala versions
We can load a newer version of Spark using the modules. In this case we will be using Spark 3.4.3:
```
module load spark/3.4.3
```

Verify the scala version used by the selected Spark version running `spark-shell`:
```
[jlopez@cdh61-login2 ~]$ spark-shell
24/08/15 18:34:10 WARN util.Utils: Service 'SparkUI' could not bind on port 4040. Attempting port 4041.
Spark context Web UI available at http://cdh61-login2.bd.cluster.cesga.es:4041
Spark context available as 'sc' (master = yarn, app id = application_1708445019134_4861).
Spark session available as 'spark'.
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /___/ .__/\_,_/_/ /_/\_\   version 3.4.3
      /_/

Using Scala version 2.12.17 (Java HotSpot(TM) 64-Bit Server VM, Java 1.8.0_191)
Type in expressions to have them evaluated.
Type :help for more information.

scala>
```
In this case we have spark 2.4.3 compiled with scala 2.12.17.

### Look for the apropriate connector
We go to the maven repository and we have to locate the required connector to use kafka with spark:
- For structured streaming we have to look in:
   - [spark-sql-kafka-0-10: Kafka 0.10+ Source For Structured Streaming](https://mvnrepository.com/artifact/org.apache.spark/spark-sql-kafka-0-10)
- For the legacy DStream API we would look for:
   - [spark-streaming-kafka-0-10: Spark Integration For Kafka 0.10](https://mvnrepository.com/artifact/org.apache.spark/spark-streaming-kafka-0-10)

In the most common case that we want to use structured streaming, we locate the connector corresponding to our spark and scala version, in our case spark 3.4.3 and scala 2.11.
- https://mvnrepository.com/artifact/org.apache.spark/spark-sql-kafka-0-10_2.12/3.4.3

In this page we look for the groupId, artifactId and version:
```
<dependency>
    <groupId>org.apache.spark</groupId>
    <artifactId>spark-sql-kafka-0-10_2.12</artifactId>
    <version>3.4.3</version>
    <scope>test</scope>
</dependency>
```

### Run spark with this connector
Then to use it we just have to pass the groupId, artifactId and version to the `--packages` option of `spark-submit` as `--packages groupId:artifactId:version` and it will download automatically the jar file:
```
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.3 your_app.py
```

For example you can use the provided example spark streaming consumer job that consumes data from a given topic (it expects the BROKER and TOPIC env variables):
```
module load spark/3.4.3
export BROKER="10.133.29.20:9092"
export TOPIC="lab2.cursoXXX"
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.3 exercises/spark_kafka_example.py
```

## References
- [Structured Streaming Kafka Integration](https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html)
